#
# Copyright (C) 2007-2013 by frePPLe bv
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from django.conf import settings
from django.db.models.functions import Cast
from django.db.models import F, FloatField, DateTimeField
from django.db.models.expressions import RawSQL
from django.template import Template
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django.utils.text import format_lazy

from freppledb.boot import getAttributeFields
from freppledb.input.models import (
    Location,
    Item,
    Supplier,
    ItemSupplier,
    PurchaseOrder,
)
from freppledb.common.report import (
    GridReport,
    GridFieldBool,
    GridFieldLastModified,
    GridFieldDateTime,
    GridFieldText,
    GridFieldHierarchicalText,
    GridFieldNumber,
    GridFieldInteger,
    GridFieldCurrency,
    GridFieldChoice,
    GridFieldDuration,
    GridFieldJSON,
)
from .utils import OperationPlanMixin

import logging

logger = logging.getLogger(__name__)


class SupplierList(GridReport):
    title = _("suppliers")
    basequeryset = Supplier.objects.all()
    model = Supplier
    frozenColumns = 1
    help_url = "modeling-wizard/purchasing/suppliers.html"
    message_when_empty = Template(
        """
        <h3>Define suppliers</h3>
        <br>
        This table contains all suppliers you are purchasing items from.<br>
        <br><br>
        <div role="group" class="btn-group.btn-group-justified">
        <a href="{{request.prefix}}/data/input/supplier/add/" class="btn btn-primary">Create a single supplier<br>in a form</a>
        <a href="{{request.prefix}}/wizard/load/production/?currentstep=4" class="btn btn-primary">Wizard to upload suppliers<br>from a spreadsheet</a>
        </div>
        <br>
        """
    )

    rows = (
        GridFieldText(
            "name",
            title=_("name"),
            key=True,
            formatter="detail",
            extra='"role":"input/supplier"',
        ),
        GridFieldText("description", title=_("description")),
        GridFieldText("category", title=_("category"), initially_hidden=True),
        GridFieldText("subcategory", title=_("subcategory"), initially_hidden=True),
        GridFieldText(
            "owner",
            title=_("owner"),
            field_name="owner__name",
            formatter="detail",
            extra='"role":"input/supplier"',
            initially_hidden=True,
        ),
        GridFieldText("source", title=_("source"), initially_hidden=True),
        GridFieldLastModified("lastmodified"),
        GridFieldText(
            "available",
            title=_("available"),
            field_name="available__name",
            formatter="detail",
            extra='"role":"input/calendar"',
            initially_hidden=True,
        ),
    )


class ItemSupplierList(GridReport):
    title = _("item suppliers")
    basequeryset = ItemSupplier.objects.all()
    model = ItemSupplier
    frozenColumns = 1
    help_url = "modeling-wizard/purchasing/item-suppliers.html"
    message_when_empty = Template(
        """
        <h3>Define item suppliers</h3>
        <br>
        This table defines which items can be procured from which supplier.<br>
        <br><br>
        <div role="group" class="btn-group.btn-group-justified">
        <a href="{{request.prefix}}/data/input/itemsupplier/add/" class="btn btn-primary">Create a single item supplier<br>in a form</a>
        <a href="{{request.prefix}}/wizard/load/production/?currentstep=4" class="btn btn-primary">Wizard to upload item suppliers<br>from a spreadsheet</a>
        </div>
        <br>
        """
    )

    rows = (
        GridFieldInteger(
            "id",
            title=_("identifier"),
            key=True,
            formatter="detail",
            extra='"role":"input/itemsupplier"',
            initially_hidden=True,
        ),
        GridFieldHierarchicalText(
            "item",
            title=_("item"),
            field_name="item__name",
            formatter="detail",
            extra='"role":"input/item"',
            model=Item,
        ),
        GridFieldHierarchicalText(
            "location",
            title=_("location"),
            field_name="location__name",
            formatter="detail",
            extra='"role":"input/location"',
            model=Location,
        ),
        GridFieldText(
            "supplier",
            title=_("supplier"),
            field_name="supplier__name",
            formatter="detail",
            extra='"role":"input/supplier"',
        ),
        GridFieldDuration("leadtime", title=_("lead time")),
        GridFieldNumber("sizeminimum", title=_("size minimum")),
        GridFieldNumber("sizemultiple", title=_("size multiple")),
        GridFieldNumber("sizemaximum", title=_("size maximum"), initially_hidden=True),
        GridFieldCurrency("cost", title=_("cost")),
        GridFieldInteger("priority", title=_("priority")),
        GridFieldDuration("fence", title=_("fence"), initially_hidden=True),
        GridFieldDateTime(
            "effective_start", title=_("effective start"), initially_hidden=True
        ),
        GridFieldDateTime(
            "effective_end", title=_("effective end"), initially_hidden=True
        ),
        GridFieldText(
            "resource",
            title=_("resource"),
            field_name="resource__name",
            formatter="detail",
            extra='"role":"input/resource"',
            initially_hidden=True,
        ),
        GridFieldNumber(
            "resource_qty", title=_("resource quantity"), initially_hidden=True
        ),
        GridFieldText("source", title=_("source"), initially_hidden=True),
        GridFieldLastModified("lastmodified"),
        # Optional fields referencing the item
        GridFieldText(
            "item__type",
            title=format_lazy("{} - {}", _("item"), _("type")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__description",
            title=format_lazy("{} - {}", _("item"), _("description")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__category",
            title=format_lazy("{} - {}", _("item"), _("category")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__subcategory",
            title=format_lazy("{} - {}", _("item"), _("subcategory")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldCurrency(
            "item__cost",
            title=format_lazy("{} - {}", _("item"), _("cost")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldNumber(
            "item__volume",
            title=format_lazy("{} - {}", _("item"), _("volume")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldNumber(
            "item__weight",
            title=format_lazy("{} - {}", _("item"), _("weight")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__owner",
            title=format_lazy("{} - {}", _("item"), _("owner")),
            field_name="item__owner__name",
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__source",
            title=format_lazy("{} - {}", _("item"), _("source")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldLastModified(
            "item__lastmodified",
            title=format_lazy("{} - {}", _("item"), _("last modified")),
            initially_hidden=True,
            editable=False,
        ),
        # Optional fields referencing the location
        GridFieldText(
            "location__description",
            title=format_lazy("{} - {}", _("location"), _("description")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "location__category",
            title=format_lazy("{} - {}", _("location"), _("category")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "location__subcategory",
            title=format_lazy("{} - {}", _("location"), _("subcategory")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "location__available",
            title=format_lazy("{} - {}", _("location"), _("available")),
            initially_hidden=True,
            field_name="location__available__name",
            formatter="detail",
            extra='"role":"input/calendar"',
            editable=False,
        ),
        GridFieldText(
            "location__owner",
            title=format_lazy("{} - {}", _("location"), _("owner")),
            initially_hidden=True,
            field_name="location__owner__name",
            formatter="detail",
            extra='"role":"input/location"',
            editable=False,
        ),
        GridFieldText(
            "location__source",
            title=format_lazy("{} - {}", _("location"), _("source")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldLastModified(
            "location__lastmodified",
            title=format_lazy("{} - {}", _("location"), _("last modified")),
            initially_hidden=True,
            editable=False,
        ),
        # Optional fields referencing the supplier
        GridFieldText(
            "supplier__description",
            title=format_lazy("{} - {}", _("supplier"), _("description")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__category",
            title=format_lazy("{} - {}", _("supplier"), _("category")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__subcategory",
            title=format_lazy("{} - {}", _("supplier"), _("subcategory")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__available",
            title=format_lazy("{} - {}", _("supplier"), _("available")),
            field_name="supplier__available__name",
            formatter="detail",
            extra='"role":"input/calendar"',
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__source",
            title=format_lazy("{} - {}", _("supplier"), _("source")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldLastModified(
            "supplier__lastmodified",
            title=format_lazy("{} - {}", _("supplier"), _("last modified")),
            initially_hidden=True,
            editable=False,
        ),
    )

    @classmethod
    def initialize(reportclass, request):
        if reportclass._attributes_added != 2:
            reportclass._attributes_added = 2
            reportclass.attr_sql = ""
            # Adding custom item attributes
            for f in getAttributeFields(
                Item, related_name_prefix="item", initially_hidden=True
            ):
                reportclass.rows += (f,)
                reportclass.attr_sql += "item.%s, " % f.name.split("__")[-1]
            # Adding custom location attributes
            for f in getAttributeFields(
                Location, related_name_prefix="location", initially_hidden=True
            ):
                reportclass.rows += (f,)
                reportclass.attr_sql += "location.%s, " % f.name.split("__")[-1]


class PurchaseOrderList(OperationPlanMixin, GridReport):
    template = "input/operationplanreport.html"
    title = _("purchase orders")
    model = PurchaseOrder
    default_sort = (1, "desc")
    frozenColumns = 1
    multiselect = True
    editable = True
    height = 250
    help_url = "modeling-wizard/purchasing/purchase-orders.html"
    message_when_empty = Template(
        """
        <h3>Define purchase orders</h3>
        <br>
        This table defines ongoing and proposed purchase orders.<br><br>
        Use this table to load ongoing purchase orders in the status "confirmed".<br><br>
        The planning algorithm will further populate this table with additional "proposed" purchase orders for the future.<br>
        <br><br>
        <div role="group" class="btn-group.btn-group-justified">
        <a href="{{request.prefix}}/data/input/purchaseorder/add/" onclick="window.location = $(event.target).attr('href')" class="btn btn-primary">Create a single purchase order<br>in a form</a>
        <a href="{{request.prefix}}/wizard/load/production/?currentstep=7" onclick="window.location = $(event.target).attr('href')" class="btn btn-primary">Wizard to upload purchase orders<br>from a spreadsheet</a>
        </div>
        <br>
        """
    )

    @classmethod
    def extra_context(reportclass, request, *args, **kwargs):
        if args and args[0]:
            request.session["lasttab"] = "purchaseorders"
            paths = request.path.split("/")
            path = paths[4]
            if path == "supplier" or request.path.startswith("/detail/input/supplier/"):
                return {
                    "active_tab": "purchaseorders",
                    "model": Supplier,
                    "title": force_text(Supplier._meta.verbose_name) + " " + args[0],
                    "post_title": _("purchase orders"),
                }
            elif path == "location" or request.path.startswith(
                "/detail/input/location/"
            ):
                return {
                    "active_tab": "purchaseorders",
                    "model": Location,
                    "title": force_text(Location._meta.verbose_name) + " " + args[0],
                    "post_title": _("purchase orders"),
                }
            elif path == "item" or request.path.startswith("/detail/input/item/"):
                return {
                    "active_tab": "purchaseorders",
                    "model": Item,
                    "title": force_text(Item._meta.verbose_name) + " " + args[0],
                    "post_title": _("purchase orders"),
                }
            elif path == "operationplanmaterial":
                return {
                    "active_tab": "purchaseorders",
                    "model": Item,
                    "title": force_text(Item._meta.verbose_name) + " " + args[0],
                    "post_title": force_text(
                        _("on order in %(loc)s at %(date)s")
                        % {"loc": args[1], "date": args[2]}
                    ),
                }
            elif path == "produced":
                return {
                    "active_tab": "purchaseorders",
                    "model": Item,
                    "title": force_text(Item._meta.verbose_name) + " " + args[0],
                    "post_title": force_text(
                        _("on order in %(loc)s between %(date1)s and %(date2)s")
                        % {"loc": args[1], "date1": args[2], "date2": args[3]}
                    ),
                }
            else:
                return {"active_tab": "edit", "model": Item}
        else:
            return {"active_tab": "purchaseorders"}

    @classmethod
    def basequeryset(reportclass, request, *args, **kwargs):
        q = PurchaseOrder.objects.all()
        if args and args[0]:
            paths = request.path.split("/")
            path = paths[4]
            if paths[4] == "operationplanmaterial":
                q = q.filter(
                    location__name=args[1],
                    item__name=args[0],
                    startdate__lt=args[2],
                    enddate__gte=args[2],
                )
            elif path == "produced":
                q = q.filter(
                    location__name=args[1],
                    item__name=args[0],
                    enddate__gte=args[2],
                    enddate__lt=args[3],
                )
            elif path == "supplier" or request.path.startswith(
                "/detail/input/supplier/"
            ):
                try:
                    Supplier.rebuildHierarchy(database=request.database)
                    sup = (
                        Supplier.objects.all().using(request.database).get(name=args[0])
                    )
                    lft = sup.lft
                    rght = sup.rght
                except Supplier.DoesNotExist:
                    lft = 1
                    rght = 1
                q = q.filter(supplier__lft__gte=lft, supplier__rght__lte=rght)
            elif path == "location" or request.path.startswith(
                "/detail/input/location/"
            ):
                try:
                    Location.rebuildHierarchy(database=request.database)
                    loc = (
                        Location.objects.all().using(request.database).get(name=args[0])
                    )
                    lft = loc.lft
                    rght = loc.rght
                except Location.DoesNotExist:
                    lft = 1
                    rght = 1
                q = q.filter(location__lft__gte=lft, location__rght__lte=rght)
            elif path == "item" or request.path.startswith("/detail/input/item/"):
                try:
                    Item.rebuildHierarchy(database=request.database)
                    itm = Item.objects.all().using(request.database).get(name=args[0])
                    lft = itm.lft
                    rght = itm.rght
                except Item.DoesNotExist:
                    lft = 1
                    rght = 1
                q = q.filter(item__lft__gte=lft, item__rght__lte=rght)

        q = reportclass.operationplanExtraBasequery(q.select_related("item"), request)
        return q.annotate(
            unit_cost=Cast(
                RawSQL(
                    """
                    coalesce((
                      select cost
                      from itemsupplier
                      where itemsupplier.item_id = operationplan.item_id
                        and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                        and itemsupplier.supplier_id = operationplan.supplier_id
                      order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                         operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                         priority <> 0,
                         priority
                      limit 1),
                     (select cost from item where item.name = operationplan.item_id), 0)
                    """,
                    [],
                ),
                output_field=FloatField(),
            ),
            total_cost=Cast(F("unit_cost") * F("quantity"), output_field=FloatField()),
            total_volume=Cast(
                F("item__volume") * F("quantity"), output_field=FloatField()
            ),
            total_weight=Cast(
                F("item__weight") * F("quantity"), output_field=FloatField()
            ),
            feasible=RawSQL(
                "coalesce((operationplan.plan->>'feasible')::boolean, true)", []
            ),
            computed_color=RawSQL(
                """
                case when operationplan.color >= 999999 and operationplan.plan ? 'item' then
                999999
                - extract(epoch from operationplan.delay)/86400.0
                + 1000000
                when operationplan.color >= 999999 and not(operationplan.plan ? 'item') then
                999999
                - extract(epoch from operationplan.delay)/86400.0
                else operationplan.color
                end
                """,
                [],
            ),
            itemsupplier_sizeminimum=Cast(
                RawSQL(
                    """
                    select sizeminimum
                    from itemsupplier
                    where itemsupplier.item_id = operationplan.item_id
                      and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                      and itemsupplier.supplier_id = operationplan.supplier_id
                    order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                       operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                       priority <> 0,
                       priority
                    limit 1
                    """,
                    [],
                ),
                output_field=FloatField(),
            ),
            itemsupplier_sizemultiple=Cast(
                RawSQL(
                    """
                    select sizemultiple
                    from itemsupplier
                    where itemsupplier.item_id = operationplan.item_id
                      and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                      and itemsupplier.supplier_id = operationplan.supplier_id
                    order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                       operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                       priority <> 0,
                       priority
                    limit 1
                    """,
                    [],
                ),
                output_field=FloatField(),
            ),
            itemsupplier_sizemaximum=Cast(
                RawSQL(
                    """
                    select sizemaximum
                    from itemsupplier
                    where itemsupplier.item_id = operationplan.item_id
                      and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                      and itemsupplier.supplier_id = operationplan.supplier_id
                    order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                       operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                       priority <> 0,
                       priority
                    limit 1
                    """,
                    [],
                ),
                output_field=FloatField(),
            ),
            itemsupplier_priority=Cast(
                RawSQL(
                    """
                    select priority
                    from itemsupplier
                    where itemsupplier.item_id = operationplan.item_id
                      and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                      and itemsupplier.supplier_id = operationplan.supplier_id
                    order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                       operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                       priority <> 0,
                       priority
                    limit 1
                    """,
                    [],
                ),
                output_field=FloatField(),
            ),
            itemsupplier_effective_start=Cast(
                RawSQL(
                    """
                    select effective_start
                    from itemsupplier
                    where itemsupplier.item_id = operationplan.item_id
                      and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                      and itemsupplier.supplier_id = operationplan.supplier_id
                    order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                       operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                       priority <> 0,
                       priority
                    limit 1
                    """,
                    [],
                ),
                output_field=DateTimeField(),
            ),
            itemsupplier_effective_end=Cast(
                RawSQL(
                    """
                    select effective_end
                    from itemsupplier
                    where itemsupplier.item_id = operationplan.item_id
                      and (itemsupplier.location_id is null or itemsupplier.location_id = operationplan.location_id)
                      and itemsupplier.supplier_id = operationplan.supplier_id
                    order by operationplan.enddate < itemsupplier.effective_end desc nulls first,
                       operationplan.enddate >= itemsupplier.effective_start desc nulls first,
                       priority <> 0,
                       priority
                    limit 1
                    """,
                    [],
                ),
                output_field=DateTimeField(),
            ),
        )

    rows = (
        GridFieldText(
            "reference",
            title=_("reference"),
            key=True,
            formatter="detail",
            extra='role:"input/purchaseorder"',
            editable=not settings.ERP_CONNECTOR,
        ),
        GridFieldNumber(
            "computed_color",
            title=_("inventory status"),
            formatter="color",
            width="125",
            editable=False,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldNumber("color", hidden=True),
        GridFieldHierarchicalText(
            "item",
            title=_("item"),
            field_name="item__name",
            formatter="detail",
            extra='"role":"input/item"',
            model=Item,
        ),
        GridFieldHierarchicalText(
            "location",
            title=_("location"),
            field_name="location__name",
            formatter="detail",
            extra='"role":"input/location"',
            model=Location,
        ),
        GridFieldHierarchicalText(
            "supplier",
            title=_("supplier"),
            field_name="supplier__name",
            formatter="detail",
            extra='"role":"input/supplier"',
            model=Supplier,
        ),
        GridFieldDateTime(
            "startdate",
            title=_("ordering date"),
            extra='"formatoptions":{"srcformat":"Y-m-d H:i:s","newformat":"Y-m-d H:i:s", "defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldDateTime(
            "enddate",
            title=_("receipt date"),
            extra='"formatoptions":{"srcformat":"Y-m-d H:i:s","newformat":"Y-m-d H:i:s", "defaultValue":""}, "summaryType":"max"',
        ),
        GridFieldNumber(
            "quantity",
            title=_("quantity"),
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"sum"',
        ),
        GridFieldChoice(
            "status",
            title=_("status"),
            choices=PurchaseOrder.orderstatus,
            editable=not settings.ERP_CONNECTOR,
        ),
        GridFieldCurrency(
            "unit_cost",
            title=format_lazy("{} - {}", _("item"), _("cost")),
            editable=False,
            search=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"max"',
        ),
        GridFieldCurrency(
            "total_cost",
            title=_("total cost"),
            editable=False,
            search=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"sum"',
        ),
        GridFieldNumber(
            "total_volume",
            title=_("total volume"),
            editable=False,
            search=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"sum"',
        ),
        GridFieldNumber(
            "total_weight",
            title=_("total weight"),
            editable=False,
            search=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"sum"',
        ),
        GridFieldText(
            "batch", title=_("batch"), editable="true", initially_hidden=True
        ),
        GridFieldNumber(
            "criticality",
            title=_("criticality"),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldDuration(
            "delay",
            title=_("delay"),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"max"',
        ),
        GridFieldJSON(
            "demands",
            title=_("demands"),
            editable=False,
            search=True,
            sortable=False,
            formatter="demanddetail",
            extra='"role":"input/demand"',
        ),
        GridFieldText("source", title=_("source"), initially_hidden=True),
        GridFieldBool(
            "feasible",
            title=_("feasible"),
            editable=False,
            initially_hidden=True,
            search=True,
        ),
        GridFieldLastModified("lastmodified"),
        # Annoted fields referencing the itemsupplier
        GridFieldNumber(
            "itemsupplier_sizeminimum",
            title=format_lazy("{} - {}", _("item supplier"), _("size minimum")),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldNumber(
            "itemsupplier_sizemultiple",
            title=format_lazy("{} - {}", _("item supplier"), _("size multiple")),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldNumber(
            "itemsupplier_sizemaximum",
            title=format_lazy("{} - {}", _("item supplier"), _("size maximum")),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldDateTime(
            "itemsupplier_effective_end",
            title=format_lazy("{} - {}", _("item supplier"), _("effective end")),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldDateTime(
            "itemsupplier_effective_start",
            title=format_lazy("{} - {}", _("item supplier"), _("effective start")),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        GridFieldNumber(
            "itemsupplier_priority",
            title=format_lazy("{} - {}", _("item supplier"), _("priority")),
            editable=False,
            initially_hidden=True,
            extra='"formatoptions":{"defaultValue":""}, "summaryType":"min"',
        ),
        # Optional fields referencing the item
        GridFieldText(
            "item__type",
            title=format_lazy("{} - {}", _("item"), _("type")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__description",
            title=format_lazy("{} - {}", _("item"), _("description")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__category",
            title=format_lazy("{} - {}", _("item"), _("category")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__subcategory",
            title=format_lazy("{} - {}", _("item"), _("subcategory")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldNumber(
            "item__volume",
            title=format_lazy("{} - {}", _("item"), _("volume")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldNumber(
            "item__weight",
            title=format_lazy("{} - {}", _("item"), _("weight")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__owner",
            title=format_lazy("{} - {}", _("item"), _("owner")),
            field_name="item__owner__name",
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "item__source",
            title=format_lazy("{} - {}", _("item"), _("source")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldLastModified(
            "item__lastmodified",
            title=format_lazy("{} - {}", _("item"), _("last modified")),
            initially_hidden=True,
            editable=False,
        ),
        # Optional fields referencing the location
        GridFieldText(
            "location__description",
            title=format_lazy("{} - {}", _("location"), _("description")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "location__category",
            title=format_lazy("{} - {}", _("location"), _("category")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "location__subcategory",
            title=format_lazy("{} - {}", _("location"), _("subcategory")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "location__available",
            title=format_lazy("{} - {}", _("location"), _("available")),
            initially_hidden=True,
            field_name="location__available__name",
            formatter="detail",
            extra='"role":"input/calendar"',
            editable=False,
        ),
        GridFieldText(
            "location__owner",
            title=format_lazy("{} - {}", _("location"), _("owner")),
            initially_hidden=True,
            field_name="location__owner__name",
            formatter="detail",
            extra='"role":"input/location"',
            editable=False,
        ),
        GridFieldText(
            "location__source",
            title=format_lazy("{} - {}", _("location"), _("source")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldLastModified(
            "location__lastmodified",
            title=format_lazy("{} - {}", _("location"), _("last modified")),
            initially_hidden=True,
            editable=False,
        ),
        # Optional fields referencing the supplier
        GridFieldText(
            "supplier__description",
            title=format_lazy("{} - {}", _("supplier"), _("description")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__category",
            title=format_lazy("{} - {}", _("supplier"), _("category")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__subcategory",
            title=format_lazy("{} - {}", _("supplier"), _("subcategory")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "supplier__owner",
            title=format_lazy("{} - {}", _("supplier"), _("owner")),
            initially_hidden=True,
            field_name="supplier__owner__name",
            formatter="detail",
            extra='"role":"input/supplier"',
            editable=False,
        ),
        GridFieldText(
            "supplier__source",
            title=format_lazy("{} - {}", _("supplier"), _("source")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldLastModified(
            "supplier__lastmodified",
            title=format_lazy("{} - {}", _("supplier"), _("last modified")),
            initially_hidden=True,
            editable=False,
        ),
        GridFieldText(
            "end_items",
            title=_("end items"),
            editable=False,
            search=False,
            sortable=False,
            initially_hidden=True,
            formatter="listdetail",
            extra='"role":"input/item"',
        ),
    )

    if settings.ERP_CONNECTOR:
        actions = [
            {
                "name": "erp_incr_export",
                "label": format_lazy("export to {erp}", erp=settings.ERP_CONNECTOR),
                "function": "ERPconnection.IncrementalExport(jQuery('#grid'),'PO')",
            }
        ]
    else:
        actions = [
            {
                "name": "proposed",
                "label": format_lazy(
                    _("change status to {status}"), status=_("proposed")
                ),
                "function": "grid.setStatus('proposed')",
            },
            {
                "name": "approved",
                "label": format_lazy(
                    _("change status to {status}"), status=_("approved")
                ),
                "function": "grid.setStatus('approved')",
            },
            {
                "name": "confirmed",
                "label": format_lazy(
                    _("change status to {status}"), status=_("confirmed")
                ),
                "function": "grid.setStatus('confirmed')",
            },
            {
                "name": "completed",
                "label": format_lazy(
                    _("change status to {status}"), status=_("completed")
                ),
                "function": "grid.setStatus('completed')",
            },
            {
                "name": "closed",
                "label": format_lazy(
                    _("change status to {status}"), status=_("closed")
                ),
                "function": "grid.setStatus('closed')",
            },
        ]

    @classmethod
    def initialize(reportclass, request):
        if reportclass._attributes_added != 2:
            reportclass._attributes_added = 2
            for f in getAttributeFields(PurchaseOrder):
                reportclass.rows += (f,)
            for f in getAttributeFields(Item, related_name_prefix="item"):
                f.editable = False
                reportclass.rows += (f,)
            for f in getAttributeFields(Location, related_name_prefix="location"):
                f.editable = False
                reportclass.rows += (f,)
            for f in getAttributeFields(Supplier, related_name_prefix="supplier"):
                f.editable = False
                reportclass.rows += (f,)
