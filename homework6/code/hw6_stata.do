clear all
set more off

local path "C:\Users\brewe\Dropbox (Personal)\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework6"
local outputpath "C:\Users\brewe\Dropbox (Personal)\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework6\output"

cd "`path'"

* Load the data

    use "energy_staggered.dta", clear

* Question 1

    * Create a cohort variable

        gen double statadate = clock(datetime, "MDYhms")

        sort statadate 

        egen time = group(statadate)

        bysort id: egen cohort2 = min(time) if treatment == 1 & devicegroup == 1
        bysort id: egen cohort = min(cohort2)
        drop cohort2

        tab cohort

        return list


        // 539 cohorts

* Question 2

    twowayfeweights energy id time treatment, type(feTR)

* Question 3

    reghdfe energy i.treatment temperature precipitation relativehumidity, absorb(id time) cluster(id)

* Daily data

    gen day = day(dofc(statadate))
    collapse (mean) temperature precipitation relativehumidity (sum) energy (max) devicegroup treatment, by(id day)

    bysort id: egen cohort2 = min(day) if treatment == 1 & devicegroup == 1
    bysort id: egen cohort = min(cohort2)
    drop cohort2

    gen time_to_treat = day - cohort
    *replace time_to_treat = 0 if missing(time_to_treat)
    
    su time_to_treat, meanonly
    forvalues i = `r(min)' / `r(max)' {
        if `i' < 0 {
            local b = `i'*(-1)
            gen lead`b' = 0
            replace lead`b' = 1 if time_to_treat == `i'
            la var lead`b' "`i'"
        }
        else {
            gen lag`i' = 0
            replace lag`i' = 1 if time_to_treat == `i'
            la var lag`i' "`i'"
        }
    }


* Question 1 Regression ATT
	
    reghdfe energy i.treatment temperature precipitation relativehumidity, absorb(id day) cluster(id)

* Question 2 Regression event study

    reghdfe energy lead29-lead2 lag* temperature precipitation relativehumidity, absorb(id day) cluster(id)

    coefplot, vertical keep(lead* lag*) yline(0) xlabel(,angle(90)) xline(28.5) title(Question 2 TWFE event study plot)
	
	cd "`outputpath'"
	graph export question2plot.pdf, replace

* Question 3 Eventdd

    eventdd energy temperature precipitation relativehumidity, method(hdfe, absorb(id day) cluster(id)) timevar(time_to_treat) 
	
	graph export question3plot.pdf, replace

* Question 4 CSDID

    gen g = cohort
    replace g = 0 if missing(g)
    di c(current_time)
    csdid energy temperature precipitation relativehumidity, i(id) t(day) gvar(g) wboot reps(50) agg(event)
    di c(current_time)
    csdid_plot
	
	graph export question4plot.pdf, replace
