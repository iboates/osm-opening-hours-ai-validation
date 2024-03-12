local srid = 4326

local tables = {}

tables.points = osm2pgsql.define_node_table('points', {
    { column = 'name', type = 'text' },
    { column = 'street', type = 'text' },
    { column = 'number', type = 'text' },
    { column = 'amenity', type = 'text' },
    { column = 'opening_hours', type = 'text' },
    { column = 'website', type = 'text' },
    { column = 'geom', type = 'point', projection = srid, not_null = true },
})

function osm2pgsql.process_node(object)
    tables.points:insert({
        name = object:grab_tag('name'),
        street = object:grab_tag('addr:street'),
        number = object:grab_tag('addr:number'),
        amenity = object:grab_tag('amenity'),
        opening_hours = object:grab_tag('opening_hours'),
        website = object:grab_tag('website'),
        geom = object:as_point()
    })
end
