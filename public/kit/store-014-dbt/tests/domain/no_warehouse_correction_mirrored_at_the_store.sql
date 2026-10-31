-- No warehouse correction is mirrored at the store
select * from {{ ref('mirror_pairs') }} where kind = 'across buildings'
