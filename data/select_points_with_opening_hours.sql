select p.*, 'de' as country_code, b.varname_1 as state
from opening_hours_germany p
left join bundeslaender b on st_intersects(p.geom, b.geom)
order by node_id
