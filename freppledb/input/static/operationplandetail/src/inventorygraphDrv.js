/*
 * Copyright (C) 2024 by frePPLe bv
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 *
 */

'use strict';

angular.module('operationplandetailapp').directive('showinventorygraphDrv', showinventorygraphDrv);

showinventorygraphDrv.$inject = ['$window', '$filter', 'gettextCatalog'];

function showinventorygraphDrv($window, $filter, gettextCatalog) {

  var directive = {
    restrict: 'EA',
    scope: { operationplan: '=data' },
    link: linkfunc
  };
  return directive;

  function linkfunc(scope, elem, attrs) {
    var template = '<div class="card-header"><h5 class="card-title text-capitalize">' +
      gettextCatalog.getString("inventory") + '</h5></div>' +
      '<div class="card-body"><table class="table table-sm table-hover table-borderless"><thead></thead></thead><tbody></tbody></table></div>';

    scope.$watchGroup(['operationplan.id', 'operationplan.inventoryreport.length'], function (newValue, oldValue) {
      // console.log(46, scope.operationplan);
      angular.element(document).find('#attributes-inventorygraph').empty().append(template);
      var rows = ['<tr><td colspan="1">' + gettextCatalog.getString('no inventory information') + '</td></tr>'];
      var columnHeaders = ['<tr></tr>'];

      if (typeof scope.operationplan !== 'undefined') {
        if (scope.operationplan.hasOwnProperty('inventoryreport')) {
          columnHeaders = ['<tr><td></td>' ];
          rows = [
            // '<tr><td><b class="text-capitalize">' + gettextCatalog.getString("bucket") + '</b></td>',
            '<tr><td><span class="text-capitalize">' + gettextCatalog.getString("start on-hand") + '</span></td>',
            '<tr><td><span class="text-capitalize">' + gettextCatalog.getString("safety stock") + '</span></td>',
            '<tr><td><span class="text-capitalize">' + gettextCatalog.getString("total consumed") + '</span></td>',
            '<tr><td><span class="px-3 text-capitalize">' + gettextCatalog.getString("consumed proposed") + '</span></td>',
            '<tr><td><span class="px-3 text-capitalize">' + gettextCatalog.getString("consumed confirmed") + '</span></td>',
            '<tr><td><span class="text-capitalize">' + gettextCatalog.getString("total produced") + '</span></td>',
            '<tr><td><span class="px-3 text-capitalize">' + gettextCatalog.getString("produced proposed") + '</span></td>',
            '<tr><td><span class="px-3 text-capitalize">' + gettextCatalog.getString("produced confirmed") + '</span></td>',
            '<tr><td><span class="text-capitalize">' + gettextCatalog.getString("end on-hand") + '</span></td>',
          ];
          angular.forEach(scope.operationplan.inventoryreport, function (inventoryData) {
              // console.log(68, inventoryData);
            columnHeaders.push('<td id="' + inventoryData[0] +
              '" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-custom-class="custom-tooltip"' +
                'data-bs-title="' + $filter('formatdate')(inventoryData[1]) + ' - ' + $filter('formatdate')(inventoryData[2])+'">' +
                '<b class="text-capitalize text-center">' + inventoryData[0] + '</b></td>'
            );

            for (const i in inventoryData.slice(4)) {
              // console.log(72, rows[i], inventoryData.slice(4)[i]);
              rows[i] += '<td>' + $filter('number')(inventoryData.slice(4)[i]) + '</td>';
            }
          });
          columnHeaders.push('</tr>');
          rows = rows.map(x => x + '</tr>');
        }
      }

      angular.element(document).find('#attributes-inventorygraph thead').append(columnHeaders.join(""));
      angular.element(document).find('#attributes-inventorygraph tbody').append(rows.join(""));
      window.tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
      window.tooltipList = [...window.tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }); //watch end

  } //link end
} //directive end
