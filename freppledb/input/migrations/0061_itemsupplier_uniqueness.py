# Copyright (C) 2021 by frePPLe bv
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

from django.db import migrations, connections


def dropExistingIndex(apps, schema_editor):
    db = schema_editor.connection.alias
    output = []
    with connections[db].cursor() as cursor:
        # delete records that will fail with the new indexes
        cursor.execute(
            """
            with cte as
            (
            select id, row_number() over(partition by item_id, supplier_id, effective_start order by cost) as rn
            from itemsupplier
            where location_id is null
            )
            delete from itemsupplier
            using cte
            where itemsupplier.id = cte.id
            and cte.rn > 1;
        """
        )
        cursor.execute(
            """
            select
                i.relname as index_name, array_agg(a.attname)
            from
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            where
                t.oid = ix.indrelid
                and i.oid = ix.indexrelid
                and a.attrelid = t.oid
                and a.attnum = ANY(ix.indkey)
                and t.relkind = 'r'
                and t.relname like 'itemsupplier'
                and ix.indisunique
            group by i.relname
            """
        )
        for i in cursor:
            if (
                "item_id" in i[1]
                and "location_id" in i[1]
                and "supplier_id" in i[1]
                and "effective_start" in i[1]
            ):

                output.append(i[0])
        if len(output) > 0:
            cursor.execute(
                "alter table itemsupplier drop constraint %s" % ",".join(output)
            )


class Migration(migrations.Migration):

    dependencies = [
        ("input", "0060_remove_like_indexes"),
    ]

    operations = [
        migrations.RunPython(dropExistingIndex),
        migrations.RunSQL(
            """
            create unique index on itemsupplier
            (item_id, location_id, supplier_id, effective_start) where location_id is not null;
            create unique index on itemsupplier
            (item_id, supplier_id, effective_start) where location_id is null;
            """
        ),
    ]