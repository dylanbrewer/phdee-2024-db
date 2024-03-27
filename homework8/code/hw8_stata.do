clear all
set more off

local datapath "C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework8"

cd "`datapath'"

use "electric_matching.dta", clear

* Generate treatment variable

	gen treatment = 0
	replace treatment = 1 if year == 2020 & month >= 3
	
* Log outcome variable

	gen logmw = log(mw)
	
* Question 1
	
	* Regression approach

		reghdfe logmw treatment temp pcp, absorb(month dow hour zone) vce(robust)
		
	* Matching approach
		
		egen zoneid = group(zone)
		
		
		preserve
			drop if month < 3
		
			teffects nnmatch (logmw temp pcp) (treatment), ematch(zoneid month dow hour) vce(robust) nneighbor(1) metric(maha)
		restore 
	
* Question 2

	reghdfe logmw treatment temp pcp, absorb(month dow hour zone year) vce(robust)

* Question 3

	gen year2020 = 0
	replace year2020 = 1 if year == 2020
	
	capture drop flag 
	capture drop nnmatch*
	teffects nnmatch (logmw temp pcp) (year2020), ematch(zoneid month dow hour) vce(robust) gen(nnmatch) nneighbor(1) metric(maha) osample(flag)

	local matchlist
	local j = wordcount(e(indexvar))
	forvalues i = 1/`j' {
		gen matchedmw`i' = logmw[nnmatch`i']
		local matchlist = "`matchlist'"+" "+"matchedmw`i'"
	}
	di "`matchlist'"

	su `matchlist'
	egen logmw_hat = rowmean(`matchlist')
	
	gen yvar = logmw-logmw_hat
	
	reg yvar treatment if year2020 == 1, vce(robust)