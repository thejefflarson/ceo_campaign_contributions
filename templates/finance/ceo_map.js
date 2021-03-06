    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAo1FSG5FcFxwjbAvjzMn_DRSwTQmyLrXXUnBi9bfEvTXJ8w45MRRjT2_c29y7wQB1MF7h5AQU-ukxrw" type="text/javascript"></script>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("jquery", "1", {uncompressed:true});
    </script>
    <script>
    var map;
    var geoXml;
    var mgr;
    var icon_img = { 'R': '{{ MEDIA_URL }}/images/red_circle.png', 'D': '{{ MEDIA_URL }}/images/blue_circle.png' };
    function initialize() {
        if (GBrowserIsCompatible()) {
            map = new GMap2(document.getElementById("map_canvas"));
            map.setCenter(new GLatLng(37.809,-96.555), 4); 
            map.addControl(new GLargeMapControl());
            setupAllMarkers();
        }
    } 
    /* test */
    function setupAllMarkers(){
            $.getJSON("{% url ceo_index %}{% for ceo in ceo_list %}{{ceo.id}}-{% endfor %}.json", 
                        function(data){ 
                                var total_donations = 956488;
                                $.each(data, 
                                function(i, item){
                                    var icon = new GIcon(G_DEFAULT_ICON);
                                    icon.image = icon_img[item.icon];
                                    icon.shadow = '';
                                    icon.iconSize = new GSize(item.total/total_donations * 10000,  item.total/total_donations * 10000);
                                    icon.iconAnchor = new GPoint(icon.iconSize.width/2, icon.iconSize.height/2);
                                    markerOptions = { icon: icon };
                                    var lat_lon = new GLatLng(item.pointlat,item.pointlong);
                                    var mrkr = new GMarker(lat_lon, markerOptions);
                                    GEvent.addListener(mrkr, "click", function() {
                                        window.location = item.url;
                                    });
                                    map.addOverlay(mrkr);
                                });
                        });
    }
    $("document").ready(function () {
        initialize();
        
    });
    </script>
