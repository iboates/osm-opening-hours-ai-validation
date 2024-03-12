--with study_area as (select st_makeenvelope(2.34212, 48.85890, 2.34212+0.01, 48.85890+0.01, 4326) as geom)
--
--select p.* from points p, study_area sa
--where ST_Intersects(p.geom, sa.geom)

with region as (select geom from regions where region = %(region)s)

select p.*, %(region)s as region
from points p, region r
where ST_Intersects(p.geom, r.geom)
order by node_id

limit %(limit)s;