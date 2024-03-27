clear all
set more off

local datapath "C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework5"
local outputpath "C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework5\output"

* Load data

	cd "`datapath'"
	import delimited "instrumentalvehicles.csv"

* Q1

	ivregress liml price car (mpg = weight), vce(robust)
	
	* Export table
	
		la var mpg "MPG"
		la var car "Sedan"
	
		cd "`outputpath'"
		outreg2 using hw5output_stata.tex, tex(frag) replace label
	
* Q2

	weakivtest