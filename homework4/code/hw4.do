clear all

set more off

local outputpath "C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework4\output"

cd "`outputpath'"

* Load data

	import delimited longdata_stata.csv, clear
	
* Question 1a

	reg bycatch treated shrimp salmon i.firm i.month, vce(cluster firm) // usually I would use reghdfe, but this illustrative
	
	estimates store model1
	
* Question 1b

	tab month, gen(month)

	su firm
	local firms = `r(max)'
	
	local varlist "bycatch treated shrimp salmon month1 month2 month3 month4 month5 month6 month7 month8 month9 month10 month11 month12 month13 month14 month15 month16 month17 month18 month19 month20 month21 month22 month23 month24"
	foreach x of local varlist {
		gen `x'_2 = .
		forvalues f = 1/`firms' {
			su `x' if firm == `f'
			replace `x'_2 = `x' - `r(mean)' if firm == `f'
		}
	}
	
	* Either of these is equivalent
	
		reg bycatch_2 treated_2 shrimp_2 salmon_2 month2_2 month3_2 month4_2 month5_2 month6_2 month7_2 month8_2 month9_2 month10_2 month11_2 month12_2 month13_2 month14_2 month15_2 month16_2 month17_2 month18_2 month19_2 month20_2 month21_2 month22_2 month23_2 month24_2, vce(cluster firm)
	
		reg bycatch_2 treated_2 shrimp_2 salmon_2 i.month, vce(cluster firm)
		
		estimates store model2
		
* Question 1c
	
	la var treated "Treated"
	la var shrimp "Shrimp"
	la var salmon "Salmon"
	
	la var treated_2 "Treated - mean"
	la var shrimp_2 "Shrimp - mean"
	la var salmon_2 "Salmon - mean"

	outreg2 [model1 model2] using hw4output_stata.tex, keep(treated shrimp salmon treated_2 shrimp_2 salmon_2) tex(frag) replace label ctitle("1a", "1b")
