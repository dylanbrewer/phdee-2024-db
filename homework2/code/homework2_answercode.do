clear all
set more off

* Set local paths

	local datapath "C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework2"
	local outputpath "C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework2\output"
	
	cd "`datapath'"
	
* Load data

	import delimited kwh.csv, clear
	
********************************************************************************
* Question 1
********************************************************************************

* Balance table

	local summarylist "electricity sqft temp"

	eststo treated: quietly estpost summarize `summarylist' if retrofit == 1
	eststo controls: quietly estpost summarize `summarylist' if retrofit == 0
	eststo diff: quietly estpost ttest `summarylist', by(retrofit) unequal
	
	cd "`outputpath'"
	
	esttab treated controls diff using summarystats.tex, tex cells("mean(pattern(1 1 0) fmt(%9.2fc) label(Mean))  b(star pattern(0 0 1) fmt(%9.2fc) label(Diff.))" "sd(pattern(1 1 0) par label(SD)) p(pattern(0 0 1) par fmt(%9.2fc) label(p-value))") stats(N obs, fmt(%9.0fc) labels("Observations")) starlevels(* 0.05 ** 0.01) mtitles(Treated Controls Difference) label replace prehead({\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi} \begin{tabular}{l*{3}{cc}} \hline) prefoot( & & & \\) postfoot(\hline \multicolumn{4}{c}{ ** p$<$0.01, * p$<$0.05} \\ \end{tabular} })
	
********************************************************************************
* Question 2
********************************************************************************

* Scatter plot

	twoway scatter electricity sqft, ytitle("Electricity consumption (kwh)") xtitle("Square feet") title(Question 2)
	graph export question2_scatterplot.pdf, replace
	
********************************************************************************
* Question 3
********************************************************************************

* Label variables

	la var electricity "Electricity (kwh)"
	la var sqft "Square feet"
	la var retrofit "Treatment"
	la var temp "Temperature"

* Regression

	reg electricity sqft retrofit temp, vce(robust)
	
* Table output
	
	outreg2 using question3_output.tex, label tex(fragment) replace