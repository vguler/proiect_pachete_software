
/*  1. Importul setului de date */
proc import datafile="/home/u64227270/startup_data.csv"
    out=work.startups
    dbms=csv
    replace;
    guessingrows=MAX;
run;

/*  2. Crearea și folosirea de formate definite de utilizator */
proc format;
    value $regionfmt
        'Europe' = '🇪🇺 Europa'
        'Asia' = ' Asia'
        'North America' = '🇺🇸 N. America'
        'South America' = '🇧🇷 S. America'
        'Australia' = '🇦🇺 Australia';
run;

data startups_fmt;
    set work.startups;
    format Region $regionfmt.;
run;

/*  3. Procesare iterativă și condițională a datelor */
data startups_segmentate;
    set startups_fmt;
    length Segment $12;
    if Employees < 100 then Segment = "Mic";
    else if Employees <= 1000 then Segment = "Mediu";
    else Segment = "Mare";
run;

proc freq data=startups_segmentate;
    tables Segment;
    title "Distribuție startup-uri pe segmente de dimensiune";
run;

proc print data=startups_segmentate (obs=10);
    var "Startup Name"n Employees Segment;
run;

/*  4. Crearea de subseturi de date */
data profitabile;
    set startups_segmentate;
    where Profitable = 1;
run;

proc print data=profitabile (obs=10);
    var "Startup Name"n Profitable Industry;
    title "Startup-uri profitabile";
run;

/*  5. Utilizarea de funcții SAS */
data startups_modificat ;
    set startups_segmentate;
    LogRevenue = log("Revenue (M USD)"n);
    An_Antiguitate = 2025 - "Year Founded";
run;

proc print data=startups_modificat (obs=10);
    var "Startup Name"n "Revenue (M USD)"n LogRevenue "Year Founded"n An_Antiguitate;
    title "Toate startup-urile cu venit logaritmat și vechime";
run;

/*  6. Combinarea seturilor de date (join) folosind proceduri SAS */
proc means data=startups_modificat noprint;
    class Region;
    var "Revenue (M USD)"n;
    output out=medii_revenue mean=MedieRevenue;
run;

data medii_revenue;
    set medii_revenue(keep=Region MedieRevenue);
run;

proc sort data=startups_modificat; by Region; run;
proc sort data=medii_revenue; by Region; run;

data startups_final;
    merge startups_modificat medii_revenue;
    by Region;
run;

proc print data=startups_final (obs=10);
    var "Startup Name"n Region "Revenue (M USD)"n MedieRevenue;
    title "Startup-uri cu venit propriu și media pe regiune";
run;

/*  7. Folosirea de proceduri statistice */
proc univariate data=startups_final;
    var "Revenue (M USD)"n "Valuation (M USD)"n Employees;
    histogram;
    title "Distribuția variabilelor numerice";
run;

/*  8. Utilizarea de proceduri pentru raportare */
proc print data=startups_final (obs=10) noobs;
    var "Startup Name"n Industry Region Segment "Revenue (M USD)"n MedieRevenue Profitable;
    title "Raport sumarizat al startup-urilor";
run;

