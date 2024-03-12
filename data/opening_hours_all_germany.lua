local srid = 4326

local tables = {}

tables.points = osm2pgsql.define_node_table('opening_hours_germany', {
    { column = 'name', type = 'text' },
    { column = 'amenity', type = 'text' },
    { column = 'opening_hours', type = 'text' },
    { column = 'geom', type = 'point', projection = srid, not_null = true },
})

function osm2pgsql.process_node(object)
    tables.points:insert({
        name = object:grab_tag('name'),
        amenity = object:grab_tag('amenity'),
        opening_hours = object:grab_tag('opening_hours'),
        geom = object:as_point()
    })
end
