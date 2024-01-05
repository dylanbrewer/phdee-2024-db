* Sample Stata code -- Dylan Brewer

* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\brewe\Dropbox (Personal)\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework1" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "C:\Users\brewe\Dropbox (Personal)\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework1\sample_code\output" 
	
	cd "`outputpath'"
	
* Download and use plotplainblind scheme

	ssc install blindschemes, all
	set scheme plotplainblind, permanently
	
* ON IAC VLAB server, you will need to uncomment this line and run this:

	*sysdir set PERSONAL \\iac.nas.gatech.edu\dbrewer30

* Generate some random data

	set seed 3709

	set obs 100 // 100 observations, so our random number generator stops at 100
	
	gen x1 = rnormal(10,10)
	gen x2 = rnormal(20,15)
	gen x3 = rnormal(15,15) // this variable we do not observe -- it is the error term
	
	la var x1 "Variable 1"
	la var x2 "Variable 2"
	la var x3 "Unobserved variable / error"
	
	gen yvar = x1*-3 + x2*11 + x3*1
	
	la var yvar "Outcome variable"

********************************************************************************
* Create summary statistics table

	* Generate estimates of mean and std dev
	
		eststo summary: estpost su x1 x2 yvar
	
	* Generate the LaTeX table using esttab in this case
	
		esttab summary using summarystats.tex, tex cells(mean(fmt(2) label(Mean)) sd(fmt(2) par label(Std. Dev.))) replace label
	
	*Stata has some really nice ways to create LaTeX tables quickly and easily.  Format here, not in LaTeX--this saves time in the long run.
	
********************************************************************************
* Kernel density twoway plot

	twoway (kdensity yvar, xtitle(Outcome variable) legend(on order(1 "Outcome variable")))
	graph export statadensity.pdf, replace
	
********************************************************************************
* Fit linear regression model

	reg yvar x1 x2 // this is the basic regression.  It calculates standard errors assuming homoskedasticity by default.
	
	* If we want to bootstrap, we can ask Stata to bootstrap for us:

		reg yvar x1 x2, vce(bootstrap, reps(1000))
	
	* If we need to bootstrap ourselves (to incorporate two steps in the estimation for example), we can draw bootstrap samples and repeatedly estimate our regression:
	
		mat betas = J(1000,3,.) // pre-allocate a matrix for the outcomes of our 1000 regressions
	
		forvalues i = 1/1000 {
			preserve // preserves the data as it was in the memory at this point
				bsample // samples with replacement up to the number of observations
				
				reg yvar x1 x2
				
				mat betas[`i',1] = _b[x1] // save both
				mat betas[`i',2] = _b[x2]
				mat betas[`i',3] = _b[_cons]
			restore // restores the data as you preserved it originally
		}
		
	* You can just use the 25th and 975th largest estimates (2.5 and 97.5 percentiles) as the confidence interval, take the standard deviation of all the estimates as the standard error, or calculate the full covariance matrix of the boostrap estimates.  You can look at the "betas" by typing "mat list betas"
	
	* What I will do is get the full covariance matrix.
	
	* You can write a program to get Stata to replace the covariance matrix with the bootstrapped covariance matrix.  Doing this will let you use postestimation commands like outreg2 that make creating tables really easy.
	
		capture program drop bootstrapsample
		program define bootstrapsample, eclass
			tempname betas betas1 betas2 betas3
			mat `betas' = J(1000,3,.)
			forvalues i = 1/1000 {
				preserve
					bsample 
					quietly: reg yvar x1 x2
					
					mat `betas'[`i',1] = _b[x1] // save both
					mat `betas'[`i',2] = _b[x2]
					mat `betas'[`i',3] = _b[_cons]
					di `i' // lets you know the progress
				restore
			}
			svmat `betas', name(temp)
				corr temp1 temp2 temp3, cov // get the covariance matrix
				mat A = r(C) // save covariance matrix
				drop temp1 temp2 temp3
				
			reg yvar x1 x2 // rerun the regression
			ereturn repost V = A // post the new covariance matrix as the covariance matrix V that Stata uses
		end
		
		bootstrapsample // runs the program we wrote
		estimates store bootreg
		
	* Write a table using outreg2
	
		outreg2 [bootreg] using sampleoutput_stata.tex, label 2aster tex(frag) dec(2) replace ctitle("Ordinary least squares")
		
* Plot coefficients using coefplot
	
	coefplot, vertical yline(0) rename(_cons = "Constant") ytitle("Coefficient estimate")
	
	graph export samplebars_stata.pdf, replace
	
	