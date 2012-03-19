/*
 * Function: fnGetDisplayNodes
 * Purpose:  Return an array with the TR nodes used for displaying the table
 * Returns:  array node: TR elements
 *           or
 *           node (if iRow specified)
 * Inputs:   object:oSettings - automatically added by DataTables
 *           int:iRow - optional - if present then the array returned will be the node for
 *             the row with the index 'iRow'
*/
$.fn.dataTableExt.oApi.fnGetDisplayNodes = function ( oSettings, iRow )
{
var anRows = [];
if ( oSettings.aiDisplay.length !== 0 ){
    if ( typeof iRow != 'undefined' ) {
        return oSettings.aoData[ oSettings.aiDisplay[iRow] ].nTr;
    }
    else {
        for ( var j=oSettings._iDisplayStart ; j<oSettings._iDisplayEnd ; j++ ){
            var nRow = oSettings.aoData[ oSettings.aiDisplay[j] ].nTr;
            anRows.push( nRow );
        }
    }
}
return anRows;
};

$.fn.dataTableExt.oApi.fnReloadAjax = function(oSettings, sNewSource) {
    oSettings.sAjaxSource = sNewSource;
    this.fnClearTable(this);
    this.oApi._fnProcessingDisplay(oSettings, true );
    var that = this;

    $.getJSON(oSettings.sAjaxSource, null, function(json){
    /* Got the data - add it to the table */
        for (var i=0; i<json.aaData.length; i++) {
            that.oApi._fnAddData(oSettings, json.aaData[i]);
        }
        oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
        that.fnDraw(that);
        that.oApi._fnProcessingDisplay(oSettings, false);
    });
}

jQuery.fn.dataTableExt.oApi.fnSetFilteringDelay = function ( oSettings, iDelay ) {
    /*
     * Inputs:      object:oSettings - dataTables settings object - automatically given
     *              integer:iDelay - delay in milliseconds
     * Usage:       $('#example').dataTable().fnSetFilteringDelay(250);
     * Author:      Zygimantas Berziunas (www.zygimantas.com) and Allan Jardine
     * License:     GPL v2 or BSD 3 point style
     * Contact:     zygimantas.berziunas /AT\ hotmail.com
     */
    var
        _that = this,
        iDelay = (typeof iDelay == 'undefined') ? 250 : iDelay;
     
    this.each( function ( i ) {
        $.fn.dataTableExt.iApiIndex = i;
        var
            $this = this, 
            oTimerId = null, 
            sPreviousSearch = null,
            anControl = $( 'input', _that.fnSettings().aanFeatures.f );
         
            anControl.unbind( 'keyup' ).bind( 'keyup', function() {
            var $$this = $this;
 
            if (sPreviousSearch === null || sPreviousSearch != anControl.val()) {
                window.clearTimeout(oTimerId);
                sPreviousSearch = anControl.val();  
                oTimerId = window.setTimeout(function() {
                    $.fn.dataTableExt.iApiIndex = i;
                    _that.fnFilter( anControl.val() );
                }, iDelay);
            }
        });
         
        return this;
    } );
    return this;
}
