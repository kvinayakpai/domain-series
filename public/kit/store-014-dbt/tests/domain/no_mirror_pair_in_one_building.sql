-- No count correction has a mirror image in the same building
select * from {{ ref('mirror_pairs') }} where kind = 'same building'
