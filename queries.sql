select * from base_experimentalproteininteraction limit 10;
select * from base_evidence limit 10;


select * from base_protein p where p.accession in ('Q8IXF0', 'Q7ZWA7');

update base_predictedproteininteraction set is_best = FALSE;

update 
   select i.first_id, i.second_id, max(i.quality)
	 from base_predictedproteininteraction i 
 group by i.first_id, i.second_id


update base_predictedproteininteraction set is_best = FALSE;
update base_predictedproteininteraction bii
   set is_best = TRUE
 where bii.id in (
  select min(bi.id) 
    from (
             select i.id, 
		            LEAST(i.first_id, i.second_id) as p1,
					GREATEST(i.first_id, i.second_id) as p2
               from base_predictedproteininteraction i
               join (  select LEAST(i.first_id, i.second_id) as p1,
					          GREATEST(i.first_id, i.second_id) as p2,
					          max(i.quality) quality
                         from base_predictedproteininteraction i 
                        --where (LEAST(i.first_id, i.second_id) = 27463 or GREATEST(i.first_id, i.second_id) = 27463)
                     group by p1, p2) mq
                 on p1 = mq.p1 
                and p2 = mq.p2
                and i.quality = mq.quality
           order by i.quality desc) bi
group by bi.p1, bi.p2);



   select i.first_id, i.second_id, max(i.quality)
     from base_predictedproteininteraction i 
    where (i.first_id = 11143 or i.second_id = 11143)
 group by i.first_id, i.second_id
 order by max(i.quality) desc;
 
   select i.id, i.first_id, i.second_id, i.quality, i.is_best
     from base_predictedproteininteraction i 
    where (i.first_id = 11143 and i.second_id = 26603)
 order by i.quality desc;
 
 select * from base_protein p where p.id = 9748;
select * from base_protein p where p.accession = 'B1NA68';

 select * from base_protein limit 10;
 
 select count(*) from base_protein;
