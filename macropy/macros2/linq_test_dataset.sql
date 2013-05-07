--- createbbc, 1, 50

CREATE TABLE bbc(
   name VARCHAR(50) NOT NULL
   ,region VARCHAR(60)
   ,area DECIMAL(10)
   ,population DECIMAL(11)
   ,gdp DECIMAL(14)
   ,PRIMARY KEY (name)
   );

--- tabbbc, 1, 50
insert into bbc values ('Afghanistan','South Asia',652225,26000000,NULL);
insert into bbc values ('Albania','Europe',28728,3200000,6656000000);
insert into bbc values ('Algeria','Middle East',2400000,32900000,75012000000);
insert into bbc values ('Andorra','Europe',468,64000,NULL);
insert into bbc values ('Angola','Africa',1250000,14500000,14935000000);
insert into bbc values ('Antigua and Barbuda','Americas',442,77000,770000000);
insert into bbc values ('Argentina','South America',2800000,39300000,146196000000);
insert into bbc values ('Armenia','Europe',29743,3000000,3360000000);
insert into bbc values ('Australia','Asia-Pacific',7700000,20300000,546070000000);
insert into bbc values ('Austria','Europe',83871,8100000,261630000000);
insert into bbc values ('Azerbaijan','Europe',86600,8500000,NULL);
insert into bbc values ('Bahamas','Americas',13939,321000,4789320000);
insert into bbc values ('Bahrain','Middle East',717,754000,9357140000);
insert into bbc values ('Bangladesh','South Asia',143998,152600000,67144000000);
insert into bbc values ('Barbados','Americas',430,272000,2518720000);
insert into bbc values ('Belarus','Europe',207595,9800000,20776000000);
insert into bbc values ('Belgium','Europe',30528,10300000,319609000000);
insert into bbc values ('Belize','Americas',22965,266000,NULL);
insert into bbc values ('Benin','Africa',112622,7100000,3763000000);
insert into bbc values ('Bhutan','South Asia',38364,2400000,1824000000);
insert into bbc values ('Bolivia','South America',1100000,9100000,NULL);
insert into bbc values ('Bosnia-Hercegovina','Europe',51129,4200000,8568000000);
insert into bbc values ('Botswana','Africa',581730,1800000,7812000000);
insert into bbc values ('Brazil','South America',8550000,182800000,564852000000);
insert into bbc values ('Brunei','Asia-Pacific',5765,374000,NULL);
insert into bbc values ('Bulgaria','Europe',110994,7800000,21372000000);
insert into bbc values ('Burkina Faso','Africa',274200,13800000,4968000000);
insert into bbc values ('Burma','Asia-Pacific',676552,50700000,NULL);
insert into bbc values ('Burundi','Africa',27816,7300000,NULL);
insert into bbc values ('Cambodia','Asia-Pacific',181035,14800000,4736000000);
insert into bbc values ('Cameroon','Africa',465458,16600000,13280000000);
insert into bbc values ('Canada','North America',9900000,32000000,908480000000);
insert into bbc values ('Cape Verde','Africa',4033,482000,853140000);
insert into bbc values ('Central African Republic','Africa',622984,3900000,NULL);
insert into bbc values ('Chad','Africa',1280000,9100000,2366000000);
insert into bbc values ('Chile','South America',756096,16200000,79542000000);
insert into bbc values ('China','Asia-Pacific',9600000,1300000000,1677000000000);
insert into bbc values ('Colombia','South America',1140000,45600000,NULL);
insert into bbc values ('Comoros','Africa',1862,812000,NULL);
insert into bbc values ('Costa Rica','Americas',51100,4300000,NULL);
insert into bbc values ('Croatia','Europe',56594,4400000,28996000000);
insert into bbc values ('Cuba','Americas',110860,11300000,NULL);
insert into bbc values ('Cyprus','Europe',9250,807000,14187060000);
insert into bbc values ('Czech Republic','Europe',78866,10200000,93330000000);
insert into bbc values ('Democratic Republic of Congo','Africa',2340000,56000000,6720000000);
insert into bbc values ('Denmark','Europe',43098,5400000,219510000000);
insert into bbc values ('Djibouti','Africa',23200,721000,NULL);
insert into bbc values ('Dominica','Americas',751,71000,259150000);
insert into bbc values ('Dominican Republic','Americas',48072,9000000,NULL);
insert into bbc values ('East Timor','Asia-Pacific',14609,857000,NULL);
--- tabbbc, 51, 50
insert into bbc values ('Ecuador','South America',272045,13400000,NULL);
insert into bbc values ('Egypt','Middle East',1000000,74900000,98119000000);
insert into bbc values ('El Salvador','Americas',21041,6700000,15745000000);
insert into bbc values ('Equatorial Guinea','Africa',28051,521000,484530000);
insert into bbc values ('Eritrea','Africa',117400,4561599,NULL);
insert into bbc values ('Estonia','Europe',45227,1300000,9113000000);
insert into bbc values ('Ethiopia','Africa',1130000,74200000,8162000000);
insert into bbc values ('Fiji','Asia-Pacific',18376,854000,NULL);
insert into bbc values ('Finland','Europe',338145,5200000,170508000000);
insert into bbc values ('Former Yugoslav Republic of Macedonia','Europe',25713,2000000,4700000000);
insert into bbc values ('France','Europe',543965,60700000,1826463000000);
insert into bbc values ('Gabon','Africa',267667,1400000,NULL);
insert into bbc values ('Georgia','Europe',69700,5000000,5200000000);
insert into bbc values ('Germany','Europe',357027,82500000,2484900000000);
insert into bbc values ('Ghana','Africa',238533,21800000,8284000000);
insert into bbc values ('Greece','Europe',131957,11000000,182710000000);
insert into bbc values ('Grenada','Americas',344,103000,NULL);
insert into bbc values ('Guatemala','Americas',108890,13000000,NULL);
insert into bbc values ('Guinea','Africa',245857,8800000,4048000000);
insert into bbc values ('Guinea-Bissau','Africa',36125,1600000,256000000);
insert into bbc values ('Guyana','South America',214969,768000,NULL);
insert into bbc values ('Haiti','Americas',27750,8500000,NULL);
insert into bbc values ('Honduras','Americas',112492,7200000,7416000000);
insert into bbc values ('Hungary','Europe',93030,9800000,81046000000);
insert into bbc values ('Iceland','Europe',103000,294000,11354280000);
insert into bbc values ('India','South Asia',3100000,1100000000,682000000000);
insert into bbc values ('Indonesia','Asia-Pacific',1900000,225300000,256842000000);
insert into bbc values ('Iran','Middle East',1650000,70700000,162610000000);
insert into bbc values ('Iraq','Middle East',438317,26500000,NULL);
insert into bbc values ('Ireland','Europe',70182,4000000,137120000000);
insert into bbc values ('Israel and Palestinian territories','Middle East',20770,3800000,4256000000);
insert into bbc values ('Italy','Europe',301338,57200000,1494064000000);
insert into bbc values ('Ivory Coast','Africa',322462,17100000,13167000000);
insert into bbc values ('Jamaica','Americas',10991,2700000,7830000000);
insert into bbc values ('Japan','Asia-Pacific',377864,127900000,4755322000000);
insert into bbc values ('Jordan','Middle East',89342,5700000,12198000000);
insert into bbc values ('Kazakhstan','Asia-Pacific',2700000,15400000,NULL);
insert into bbc values ('Kenya','Africa',582646,32800000,15088000000);
insert into bbc values ('Kiribati','Asia-Pacific',810,85000,82450000);
insert into bbc values ('Kuwait','Middle East',17818,2700000,48519000000);
insert into bbc values ('Kyrgyzstan','Asia-Pacific',199900,5300000,NULL);
insert into bbc values ('Laos','Asia-Pacific',236800,5900000,2301000000);
insert into bbc values ('Latvia','Europe',64589,2300000,NULL);
insert into bbc values ('Lebanon','Middle East',10452,3800000,18924000000);
insert into bbc values ('Lesotho','Africa',30355,1800000,1332000000);
insert into bbc values ('Liberia','Africa',99067,3600000,396000000);
insert into bbc values ('Libya','Africa',1770000,5800000,25810000000);
insert into bbc values ('Liechtenstein','Europe',160,34000,NULL);
insert into bbc values ('Lithuania','Europe',65300,3400000,19516000000);
insert into bbc values ('Luxembourg','Europe',2586,465000,26146950000);
--- tabbbc, 101, 50
insert into bbc values ('Madagascar','Africa',587041,18400000,5520000000);
insert into bbc values ('Malawi','Africa',118484,12600000,2142000000);
insert into bbc values ('Malaysia','Asia-Pacific',329847,25300000,NULL);
insert into bbc values ('Mali','Africa',1250000,13800000,4968000000);
insert into bbc values ('Malta','Europe',316,397000,4863250000);
insert into bbc values ('Marshall Islands','Asia-Pacific',181,57000,135090000);
insert into bbc values ('Mauritania','Middle East',1040000,3100000,1302000000);
insert into bbc values ('Mauritius','Africa',2040,1200000,5568000000);
insert into bbc values ('Mexico','North America',1960000,106400000,720328000000);
insert into bbc values ('Micronesia','Asia-Pacific',700,111000,NULL);
insert into bbc values ('Moldova','Europe',33800,4300000,3053000000);
insert into bbc values ('Monaco','Europe',2,32000,NULL);
insert into bbc values ('Mongolia','Asia-Pacific',1560000,2700000,NULL);
insert into bbc values ('Morocco','Middle East',710850,31600000,48032000000);
insert into bbc values ('Mozambique','Africa',812379,19500000,4875000000);
insert into bbc values ('Namibia','Africa',824292,2000000,4740000000);
insert into bbc values ('Nauru','Asia-Pacific',21,9900,NULL);
insert into bbc values ('Nepal','South Asia',147181,26300000,6838000000);
insert into bbc values ('New Zealand','Asia-Pacific',270534,4000000,81240000000);
insert into bbc values ('Nicaragua','Americas',120254,5700000,4503000000);
insert into bbc values ('Niger','Africa',1270000,12900000,2967000000);
insert into bbc values ('Nigeria','Africa',923768,130200000,50778000000);
insert into bbc values ('North Korea','Asia-Pacific',122762,22900000,NULL);
insert into bbc values ('Norway','Europe',323759,4600000,239338000000);
insert into bbc values ('Oman','Middle East',309500,3000000,23670000000);
insert into bbc values ('Pakistan','South Asia',796095,161100000,96660000000);
insert into bbc values ('Palau','Asia-Pacific',508,20000,NULL);
insert into bbc values ('Panama','Americas',75517,3200000,NULL);
insert into bbc values ('Papua New Guinea','Asia-Pacific',462840,5900000,3422000000);
insert into bbc values ('Paraguay','South America',406752,6200000,NULL);
insert into bbc values ('Peru','South America',1280000,28000000,NULL);
insert into bbc values ('Poland','Europe',312685,38500000,234465000000);
insert into bbc values ('Portugal','Europe',92345,10500000,150675000000);
insert into bbc values ('Qatar','Middle East',11437,628000,NULL);
insert into bbc values ('Republic of Congo','Africa',342000,3039126,NULL);
insert into bbc values ('Romania','Europe',238391,22200000,64824000000);
insert into bbc values ('Russia','Europe',17000000,141500000,482515000000);
insert into bbc values ('Rwanda','Africa',26338,8600000,1892000000);
insert into bbc values ('Samoa','Asia-Pacific',2831,182000,NULL);
insert into bbc values ('San Marino','Europe',61,27000,NULL);
insert into bbc values ('Sao Tome and Principe','Africa',1001,169000,62530000);
insert into bbc values ('Saudi Arabia','Middle East',2240000,25600000,267008000000);
insert into bbc values ('Senegal','Africa',196722,10600000,7102000000);
insert into bbc values ('Serbia and Montenegro','Europe',102173,10500000,27510000000);
insert into bbc values ('Seychelles','Africa',455,76000,NULL);
insert into bbc values ('Sierra Leone','Africa',71740,5300000,1060000000);
insert into bbc values ('Singapore','Asia-Pacific',660,4400000,106568000000);
insert into bbc values ('Slovakia','Europe',49033,5400000,34992000000);
insert into bbc values ('Slovenia','Europe',20273,2000000,29620000000);
insert into bbc values ('Solomon Islands','Asia-Pacific',27556,504000,277200000);
--- tabbbc, 151, 50
insert into bbc values ('Somalia','Africa',637657,10700000,NULL);
insert into bbc values ('South Africa','Africa',1220000,45300000,164439000000);
insert into bbc values ('South Korea','Asia-Pacific',99313,48200000,673836000000);
insert into bbc values ('Spain','Europe',505988,44100000,935361000000);
insert into bbc values ('Sri Lanka','South Asia',65610,19400000,19594000000);
insert into bbc values ('St Kitts and Nevis','Americas',269,46000,NULL);
insert into bbc values ('St Lucia','Americas',616,152000,655120000);
insert into bbc values ('St Vincent and the Grenadines','Americas',389,121000,441650000);
insert into bbc values ('Sudan','Middle East',2500000,35000000,18550000000);
insert into bbc values ('Surinam','South America',163265,442000,NULL);
insert into bbc values ('Swaziland','Africa',17364,1100000,1826000000);
insert into bbc values ('Sweden','Europe',449964,8900000,318353000000);
insert into bbc values ('Switzerland','Europe',41284,7100000,342433000000);
insert into bbc values ('Syria','Middle East',185180,18600000,22134000000);
insert into bbc values ('Taiwan','Asia-Pacific',36188,22700000,302364000000);
insert into bbc values ('Tajikistan','Asia-Pacific',143100,6300000,NULL);
insert into bbc values ('Tanzania','Africa',945087,38400000,NULL);
insert into bbc values ('Thailand','Asia-Pacific',513115,64100000,162814000000);
insert into bbc values ('The Gambia','Africa',11295,1500000,NULL);
insert into bbc values ('The Maldives','South Asia',298,338000,848380000);
insert into bbc values ('The Netherlands','Europe',41864,16300000,516710000000);
insert into bbc values ('The Philippines','Asia-Pacific',300000,82800000,96876000000);
insert into bbc values ('Togo','Africa',56785,5100000,1938000000);
insert into bbc values ('Tonga','Asia-Pacific',748,106000,NULL);
insert into bbc values ('Trinidad and Tobago','Americas',5128,1300000,NULL);
insert into bbc values ('Tunisia','Middle East',164150,10000000,26300000000);
insert into bbc values ('Turkey','Europe',779452,73300000,274875000000);
insert into bbc values ('Turkmenistan','Asia-Pacific',488100,5000000,NULL);
insert into bbc values ('Tuvalu','Asia-Pacific',26,10000,NULL);
insert into bbc values ('Uganda','Africa',241038,27600000,7452000000);
insert into bbc values ('Ukraine','Europe',603700,47800000,60228000000);
insert into bbc values ('United Arab Emirates','Middle East',77700,3100000,NULL);
insert into bbc values ('United Kingdom','Europe',242514,59600000,2022824000000);
insert into bbc values ('United States of America','North America',9800000,295000000,12213000000000);
insert into bbc values ('Uruguay','South America',176215,3500000,NULL);
insert into bbc values ('Uzbekistan','Asia-Pacific',447400,26900000,NULL);
insert into bbc values ('Vanuatu','Asia-Pacific',12190,222000,297480000);
insert into bbc values ('Vatican','Europe',0,NULL,NULL);
insert into bbc values ('Venezuela','South America',881050,26600000,NULL);
insert into bbc values ('Vietnam','Asia-Pacific',329247,83600000,45980000000);
insert into bbc values ('Yemen','Middle East',536869,21500000,12255000000);
insert into bbc values ('Zambia','Africa',752614,11000000,4950000000);
insert into bbc values ('Zimbabwe','Africa',390759,12900000,6192000000);


CREATE TABLE movie (
  id int(11) NOT NULL,
  title varchar(50) DEFAULT NULL,
  yr int(11) DEFAULT NULL,
  director int(11) DEFAULT NULL,
  budget int(11) DEFAULT NULL,
  gross int(11) DEFAULT NULL,
  PRIMARY KEY (id)
);

insert into movie values (10001, '$', 1971, 3, null, null);
insert into movie values (10002, '"Crocodile" Dundee', 1986, 19, null, 328203506);
insert into movie values (10003, '"Crocodile" Dundee II', 1988, 36, 15800000, 239606210);
insert into movie values (10004, 'Til There Was You', 1997, 49, 10000000, null);
insert into movie values (10005, 'Til We Meet Again', 1940, 65, null, null);
insert into movie values (10006, 'Adalen 31', 1969, 77, null, null);
insert into movie values (10007, 'Eon Flux', 2005, 82, 62000000, 52304001);
insert into movie values (10008, '500 Days of Summer', 2009, 95, 7500000, 60722734);
insert into movie values (10009, '(Untitled)', 2009, 107, null, null);
insert into movie values (10010, '*batteries not included', 1987, 115, 25000000, 65088797);
insert into movie values (10011, '10,000 BC', 2008, 121, 105000000, null);
insert into movie values (10012, '101 Dalmatians', 1996, 139, null, 320689294);
insert into movie values (10013, '101 Dalmatians II: Patchs London Adventure', 2003, 148, null, null);
insert into movie values (10014, '101 Reykjavík', 2000, 163, null, 126404);
insert into movie values (10015, '102 Dalmatians', 2000, 169, 85000000, 183611771);
insert into movie values (10016, '10', 1979, 177, 74856000, null);
insert into movie values (10017, '10 Rillington Place', 1971, 184, null, null);
insert into movie values (10018, '10 Things I Hate About You', 1999, 204, 16000000, 53478166);
insert into movie values (10019, '10 to Midnight', 1983, 219, null, null);
insert into movie values (10020, '11:14', 2003, 228, 6000000, null);
insert into movie values (10021, '127 Hours', 2011, 242, 18000000, 60738797);
insert into movie values (10022, '12', 2007, 250, 2500000, 4000000);
insert into movie values (10023, '12 Angry Men', 1957, 261, 350000, null);
insert into movie values (10024, '12 Monkeys', 1995, 273, 29500000, 168839459);
insert into movie values (10025, '12 Rounds', 2009, 289, 20000000, 18184083);
insert into movie values (10026, '12th & Delaware', 2010, 296, null, null);
insert into movie values (10027, '13 Ghosts', 1960, 297, null, null);
insert into movie values (10028, '13 Going on 30', 2004, 305, 37000000, 96455697);
insert into movie values (10029, '13 Moons', 2002, 323, null, null);
insert into movie values (10030, '13 Rue Madeleine', 1947, 330, null, null);
insert into movie values (10031, '1408', 2007, 339, 25000000, 131998242);
insert into movie values (10032, '1492: Conquest of Paradise', 1992, 351, null, null);
insert into movie values (10033, '15 Maiden Lane', 1936, 355, null, null);
insert into movie values (10034, '15 Minutes', 2001, 363, null, 56359980);
insert into movie values (10035, '16 Blocks', 2006, 383, null, 65664721);
insert into movie values (10036, '1732 Høtten', 1998, 397, null, null);
insert into movie values (10037, '1776', 1972, 401, null, null);
insert into movie values (10038, '17 Again', 2009, 426, 20000000, 136267476);
insert into movie values (10039, '17th Parallel: Vietnam in War', 1968, 447, null, null);
insert into movie values (10040, '1900', 1976, 464, 9000000, 6064026);
insert into movie values (10041, '1969', 1988, 501, null, null);
insert into movie values (10042, 'THE AMaZING 1984', 1956, 505, null, null);
insert into movie values (10043, '1991: The Year Punk Broke', 1992, 519, null, null);
insert into movie values (10044, '20000 Leagues Under the Sea', 1916, 544, null, null);
insert into movie values (10045, '20,000 Leagues Under the Sea', 1954, 184, 4300000, 11267000);
insert into movie values (10046, '20,000 Years in Sing Sing', 1932, 559, null, null);
insert into movie values (10047, '2001: A Space Odyssey', 1968, 565, 10500000, 56715371);
insert into movie values (10048, '200 Motels', 1971, 580, 679000, null);
insert into movie values (10049, '2010', 1984, 584, 28000000, null);
insert into movie values (10050, '2012', 2009, 121, 200000000, 769679473);

CREATE TABLE actor (
  id int(11) NOT NULL,
  name varchar(50) DEFAULT NULL,
  PRIMARY KEY (id)
);

insert into actor values (30509, 'Tori Amos');
insert into actor values (2, '');
insert into actor values (35329, 'Barbara Leake');
insert into actor values (12445, 'Don Pike');
insert into actor values (41202, 'Jill Remez');
insert into actor values (29400, 'Elsa Peterson');
insert into actor values (14241, 'Mary-Kate and Ashley Olsen');
insert into actor values (2131, 'Eve Brent');
insert into actor values (690, 'Christopher Eccleston');
insert into actor values (27966, 'Sir Ian McKellen');
insert into actor values (20773, 'Tony Genaro');
insert into actor values (43733, 'Christopher Witty');
insert into actor values (35232, 'Roland Gift');
insert into actor values (20205, 'Phil Davis');
insert into actor values (25790, 'Alexandra Monvoisin');
insert into actor values (24003, 'Suzanne Barnes');
insert into actor values (25730, 'Dominique Blanc');
insert into actor values (13640, 'Laraine Humphrys');
insert into actor values (45069, 'The Guard Brothers');
insert into actor values (15185, 'Philip Quast');
insert into actor values (41214, 'Myrtle Anderson');
insert into actor values (35763, 'Phillip Jarrett');
insert into actor values (2838, 'Whit Hertford');
insert into actor values (18714, 'Robert Conway');
insert into actor values (2487, 'Salli Richardson');
insert into actor values (44061, 'Lev Atamanov');
insert into actor values (29767, 'Ashley Williams');
insert into actor values (7743, 'Patrick Aherne');
insert into actor values (116, 'Hume Cronyn');
insert into actor values (38875, 'Kevin McKenzie');
insert into actor values (33430, 'Klaus Voormann');
insert into actor values (29933, 'Joel Gordon');
insert into actor values (8352, 'Hugh Quarshie');
insert into actor values (31272, 'Denzel Whitaker');
insert into actor values (41840, 'Ben Hollingsworth');
insert into actor values (40090, 'Jonathan Estrin');
insert into actor values (22067, 'Harold Waite');
insert into actor values (18406, 'Richard Panebianco');
insert into actor values (35292, 'Yoshiaki Hanayagi');
insert into actor values (22659, 'Alan North');
insert into actor values (2179, 'Michael Vale');
insert into actor values (22859, 'Risë Stevens');
insert into actor values (39507, 'Bill Hayes');
insert into actor values (19225, 'Kulbhushan Kharbanda');
insert into actor values (4358, 'Wendie Malick');
insert into actor values (21949, 'Katherine Bailess');
insert into actor values (6518, 'Jay Johnston');
insert into actor values (17700, 'Michael Cimino');
insert into actor values (11672, 'Tyrone Power, Sr.');
insert into actor values (334, 'Frank Latimore');

CREATE TABLE casting (
  movieid int(11) NOT NULL DEFAULT '0',
  actorid int(11) NOT NULL DEFAULT '0',
  ord int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (movieid,actorid,ord)
);

insert into casting values (10001,	4,	1);
insert into casting values (10001,	5,	2);
insert into casting values (10001,	6,	3);
insert into casting values (10001,	7,	4);
insert into casting values (10001,	8,	5);
insert into casting values (10001,	9,	6);
insert into casting values (10001,	10,	7);
insert into casting values (10001,	11,	8);
insert into casting values (10001,	12,	9);
insert into casting values (10001,	13,	10);
insert into casting values (10001,	14,	11);
insert into casting values (10001,	15,	12);
insert into casting values (10001,	16,	13);
insert into casting values (10001,	17,	14);
insert into casting values (10001,	18,	15);
insert into casting values (10002,	20,	1);
insert into casting values (10002,	21,	2);
insert into casting values (10002,	22,	3);
insert into casting values (10002,	23,	4);
insert into casting values (10002,	24,	5);
insert into casting values (10002,	25,	6);
insert into casting values (10002,	26,	7);
insert into casting values (10002,	27,	8);
insert into casting values (10002,	28,	9);
insert into casting values (10002,	29,	10);
insert into casting values (10002,	30,	11);
insert into casting values (10002,	31,	12);
insert into casting values (10002,	32,	13);
insert into casting values (10002,	33,	14);
insert into casting values (10002,	34,	15);
insert into casting values (10002,	35,	16);
insert into casting values (10003,	20,	4);
insert into casting values (10003,	21,	2);
insert into casting values (10003,	22,	3);
insert into casting values (10003,	25,	11);
insert into casting values (10003,	26,	12);
insert into casting values (10003,	37,	1);
insert into casting values (10003,	38,	5);
insert into casting values (10003,	39,	6);
insert into casting values (10003,	40,	7);
insert into casting values (10003,	41,	8);
insert into casting values (10003,	42,	9);
insert into casting values (10003,	43,	10);
insert into casting values (10003,	44,	13);
insert into casting values (10003,	45,	14);
insert into casting values (10003,	46,	15);
insert into casting values (10003,	47,	16);
insert into casting values (10003,	48,	17);
insert into casting values (10004,	50,	1);
insert into casting values (10004,	51,	2);
