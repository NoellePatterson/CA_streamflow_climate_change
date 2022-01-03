#################
# Written by Noelle Patterson, UC Davis Water Management Lab, 2020.
# Intake gridded annual climate data for California, apply intensity shifts for precipitation
# in grids representing Merced River Basin, and output the results for Merced River Basin only. 
#################

#################
### FUNCTIONS ###
#################

set_run_parameters <- function(run_number){
  # pull in csv with run params
  params_file <- read.csv("data_inputs/precip_runs.csv")
  # assign param vals based on run number
  run_params <- params_file[run_number,]
  # output list with all params 
  return(list(run_params))
}

separate_days <- function(precip_all_grids, grid_num){
  # Function takes in native data format (all 4868 CA grids for a year in one long vector,
  # not directly chronological), and returns a chronologic vector for the grid number specified.
  # Grid number is any number 1-4868 corresponding to a particular 1/16th degree grid in CA.
  locs = seq(1, length(precip_all_grids), 4868) + grid_num - 1
  grid = precip_all_grids[c(locs)]
  return(grid)
}

list_all_grids <- function(files){
  # Function takes all original data and reformats into 4868 lists (one for each grid), each 
  # containing 64 lists (one for each year) of precip data. 
  all_grids <- vector(mode = "list", length = 4868)
  # loop through each grid 
  for(grid_count in seq(length(all_grids))){
    # populate each grid with its 64-yr timeseries
    grid <- vector(mode = "list", length = 64)
    for(year_count in 1:64){
      # Pull out values for precip columns
      precip <- separate_days(files[[year_count]][,6], grid_count)
      # insert first year as first entry in grid
      grid[[year_count]] <- precip
    }
    all_grids[[grid_count]] <- grid
  }
  return(all_grids)
}

list_grids_merced <- function(files, merced_indices){
  # Function takes all original data and reformats into 4868 lists (one for each grid), each 
  # containing 64 lists (one for each year), with 8 columns of climate data. 
  all_merced_grids <- vector(mode = "list", length = 100)
  # loop through each grid 
  for(grid_count in seq(length(merced_indices))){
    # populate each grid with its 64-yr timeseries
    grid <- vector(mode = "list", length = 64)
    for(year_count in 1:64){
      # Pull out values for all eight columns, can choose which cols to return in output
      lon <- separate_days(files[[year_count]][,1], merced_indices[[grid_count]])
      lat <- separate_days(files[[year_count]][,2], merced_indices[[grid_count]])
      year <- separate_days(files[[year_count]][,3], merced_indices[[grid_count]])
      mon <- separate_days(files[[year_count]][,4], merced_indices[[grid_count]])
      day <- separate_days(files[[year_count]][,5], merced_indices[[grid_count]])
      precip <- separate_days(files[[year_count]][,6], merced_indices[[grid_count]])
      tmax <- separate_days(files[[year_count]][,7], merced_indices[[grid_count]])
      tmin <- separate_days(files[[year_count]][,8], merced_indices[[grid_count]])
      temp <- (tmin + tmax)/2 # model requires average temp, caclulate as avg of min and max
      # insert first year as first entry in grid
      grid[[year_count]] <- cbind(lon, lat, year, mon, day, precip, temp)
      # repeat for all years (put process into for loop or apply func)
    }
    all_merced_grids[[grid_count]] <- grid
  }
  return(all_merced_grids)
}

list_merced_indices <- function(files){
  # Function takes all original data and reformats into 100 lists (one for each Merced grid), 
  # each containing 64 lists (one for each year), each containing a 365/366 day precip trace. 
  merced <- read.delim("data_inputs/Merced_grids_16.txt", header=FALSE, sep="")
  m_lat <- merced[,1]
  m_lon <- merced[,2]
  test_year <- files[[1]]
  unique_grids <- test_year[1:4868,]
  # identify merced grids out of the total 4868, save all merced indices in a list
  merced_indices <- list()
  for(index in seq(length(merced[,1]))){
    r <- unique_grids[unique_grids$lon == m_lon[index] & unique_grids$lat == m_lat[index],]
    ind <- rownames(r)
    merced_indices <- append(merced_indices, as.integer(ind))
  }
  # Loop through each grid, then loop through each year, adding the rows for that grid/year
  merced_grids <- list()
  for(grid in merced_indices){
    merced_grid <- list()
    locs = seq(grid, length(files[[1]][,1]), 4868)
    for(year in seq(length(files))){
      # correct data is every nth row of year file (corresponding to a grid out of 4868 sequence)
      year_data <- files[[year]][locs, 6] # sixth column is precip
      merced_grid <- append(merced_grid, list(year_data))
    } 
    # save all years to grid file once finished
    merced_grids <- append(merced_grids, list(merced_grid))
  }
  return(list(merced_indices, merced_grids))
}

convert_grids_to_files <- function(files, grid_list){
  # Function to put grid-based chronologic precip data back into native data format.
  for(file_num in seq(1:length(files))){
    # in each file, go through each grid
    for(grid_num in seq(1:length(grid_list))){
      # for first file, put each grid's first list values into 4868th file vals
      locs = seq(1, length(files[[file_num]][,6]), 4868) + grid_num - 1
      files[[file_num]][,6][locs] <- grid_list[[grid_num]][[file_num]]
    }
  } 
  return(files)
}

add_warmup_years <- function(grid_format){
  grid_format_updated <- grid_format
  # find median annual precip year from 64-year datasets (use a representative grid)
  years <- list(rep(NA, 64))
  years_total <- rep(years, 100) # summed annual precip across all 100 grids
  for(grid in seq(length(grid_format))){ # loop thru grids (100)
    for(year in seq(length(grid_format[[1]]))){ # loop thru years (64)
      p <- grid_format[[grid]][[year]][,6]
      p_sum <- sum(p)
      years_total[[grid]][year] <- p_sum
    }
  }
  add <- function(x) Reduce("+", x)
  years_total_sums <- add(years_total)
  med <- median(years_total_sums[1:63]) # Take median of odd-number from dataset, to return a val within the dataset
  loc <- which(years_total_sums==med)
  # add median year to beginning of each grid years list, six times
  for(grid in seq(length(grid_format))){
    med_grid <- grid_format[[grid]][loc]
    med_grids <- rep(med_grid, 6)
    grid_format_updated[[grid]] <- do.call(c, list(med_grids, grid_format[[grid]]))
  } 
  return(grid_format_updated)
} 

perc_wet_days_calc <- function(annual_data){
  # Function to calc the percent of precip in the year's three highest days.
  high_days <- rev(sort(annual_data))[1:3]
  high_days_perc <- sum(high_days)/sum(annual_data)
  return(high_days_perc)
}

perc_wet_months_calc <- function(annual_data){
  # Function to calc the percentage of precip occuring in Nov-March months.
  wet_months_loc <- c(1:91, 306:length(annual_data)) # Nov-March
  wet_month_perc <- sum(annual_data[wet_months_loc])/sum(annual_data)
  return(wet_month_perc)
}

calc_sd_annual <- function(all_data){
  # Calculate standard deviation across annual precipitation. 
  year_cums <- unlist(lapply(all_data, sum))
  sd_annual <- sd(year_cums)
  return(sd_annual)
}

get_perc_20th80th <- function(all_data){
  # calculate 20th and 80th percentiles of annual precip across entire POR (64 years)
  perc_20th <- rep(NA, 4868)
  perc_80th <- rep(NA, 4868)
  for(grid in seq(1:length(perc_20th))){
    year_sums <- unlist(lapply(all_data[[grid]], sum))
    perc_20th[grid] <- quantile(year_sums, probs=c(0.2))
    perc_80th[grid] <- quantile(year_sums, probs=c(0.8))
  }
  perc_20th80th <- list(perc_20th, perc_80th)
  return(perc_20th80th)
}

calc_metric_20th <- function(all_data, perc_20th){
  # Calc number of years below 20th percentile (of orig precip)
  # perc20th specific to this grid are input as single values
  year_sums <- unlist(lapply(all_data, sum))
  count <- 0
  for(year in year_sums){
    if(year < perc_20th){
      count <- count + 1
    } 
  }
  return(count/length(year_sums))
}

calc_metric_80th <- function(all_data, perc_80th){
  # Calc number of years above 80th percentile (of orig precip)
  # perc80th specific to this grid are input as single values
  year_sums <- unlist(lapply(all_data, sum))
  count <- 0
  for(year in year_sums){
    if(year > perc_80th){
      count <- count + 1
      } 
  }
  return(count/length(year_sums))
}
  
create_summary <- function(files, orig_files){
  # Function to calculate summary metrics for adjusted vs. original precip values. 
  # Metric defs: cumulative = total precip in entire POR. 
  # perc_wet_months: percentage of precip in Nov-Mar
  # perc_wet_days: percentate of precip in three highest days of the year
  # 20th/80th_perc: number of years above 80th perc or below 20th perc (percentiles based on original data)
  summary_df <- data.frame("Metric" = c("mean", "median", "cumulative", "sd_daily", "sd_annual", 
                                        "perc_wet_months", "perc_wet_days", "20th_perc", "80th_perc"))
  summary_df$original <- NA
  grid_list <- list_all_grids(files)
  grid_list_orig <- list_all_grids(orig_files)
  # calculate 20th and 80th annual percentiles of original data, to use in 20th/80th calc
  perc_20th_80th <- get_perc_20th80th(grid_list_orig)
  perc_20th_val <- perc_20th_80th[1]
  perc_80th_val <- perc_20th_80th[2]
  
  # create variables for metrics needing daily data. One element in list for each year. 
  mean_stat <- rep(NA, 4868)
  median_stat <- rep(NA, 4868)
  cumul <- rep(NA, 4868)
  sd_daily <- rep(NA, 4868)
  perc_wet_days <- rep(NA, 4868)
  perc_wet_months <- rep(NA, 4868)
  sd_annual <- rep(NA, 4868)
  perc_20th <- rep(NA, 4868)
  perc_80th <- rep(NA, 4868)

  # populate summary data grids with x annual vals in list, to average later
  for(count in seq(1:length(mean_stat))){
    mean_stat[count] <- list(rep(NA, 6))
    median_stat[count] <- list(rep(NA, 6))
    cumul[count] <- list(rep(NA, 6))
    sd_daily[count] <- list(rep(NA, 6))
    perc_wet_days[count] <- list(rep(NA, 6))
    perc_wet_months[count] <- list(rep(NA, 6))
  }
  # populate summary data grids: one value for each year, for each grid
  for(grid in seq(1:length(mean_stat))){
    mean_stat[[grid]] <- unlist(lapply(grid_list[[grid]], mean))
    median_stat[[grid]] <- unlist(lapply(grid_list[[grid]], median))
    cumul[[grid]] <- unlist(lapply(grid_list[[grid]], sum))
    sd_daily[[grid]] <- unlist(lapply(grid_list[[grid]], sd))
    perc_wet_days[[grid]] <- unlist(lapply(grid_list[[grid]], perc_wet_days_calc))
    perc_wet_months[[grid]] <- unlist(lapply(grid_list[[grid]], perc_wet_months_calc))
    sd_annual[[grid]] <- calc_sd_annual(grid_list[[grid]])
    perc_20th[[grid]] <- calc_metric_20th(grid_list[[grid]], perc_20th_val[[1]][[grid]])
    perc_80th[[grid]] <- calc_metric_80th(grid_list[[grid]], perc_80th_val[[1]][[grid]])
  }
  # average annual stats, where necessary
  for(grid in seq(1:length(mean_stat))){
    mean_stat[[grid]] <- mean(mean_stat[[grid]])
    median_stat[[grid]] <- mean(median_stat[[grid]])
    cumul[[grid]] <- mean(cumul[[grid]])
    sd_daily[[grid]] <- mean(sd_daily[[grid]])
    perc_wet_days[[grid]] <- mean(perc_wet_days[[grid]])
    perc_wet_months[[grid]] <- mean(perc_wet_months[[grid]])
  }
  # create por metrics
  cb <- cbind(mean_stat, median_stat, cumul, sd_daily, perc_wet_days, perc_wet_months, sd_annual, perc_20th, perc_80th)
  summary_df <- data.frame(cb)
  return(summary_df)
}

intra_precip_manip <- function(annual_precip, run_parameters){
  # Function for modifying precip intensity within a year, input is a one-year precip timeseries
  # Adjust proportion of precip in wet months while keeping total precip the same. 
  
  # set intensity parameters
  wet_percent = unlist(run_parameters[[1]]["wet_percent"]) # val 0-1, percent increase in wet season precip
  highprecip_perc = unlist(run_parameters[[1]]["highprecip_perc"]) # val 0-1, percent increase in precip of three highest days
  
  # sum up precip from April - Oct (dry season)
  wet = c(1:91, 306:length(annual_precip)) # Nov-March
  dry = c(92:305) # April - Oct
  
  # create backup of original annual precip
  orig_annual_precip <- annual_precip
  orig_wet_precip <- sum(orig_annual_precip[wet])
  annual_cum <- sum(annual_precip)
  # calculate final target of volume of precip in dry and wet months
  final_wet_vol <- orig_wet_precip + (orig_wet_precip * wet_percent)
  final_dry_vol <- annual_cum - final_wet_vol
  
  # calculate current vol in dry months, and difference to target
  current_dry_vol <- sum(annual_precip[dry])
  dry_diff <- current_dry_vol - final_dry_vol
  perc_dry_reduce <- final_dry_vol/current_dry_vol
  # Apply reduction percentage across all dry season, save harvest amt for later
  annual_precip[dry] <- annual_precip[dry] * perc_dry_reduce
  dry_harvest <- sum(orig_annual_precip[dry] - annual_precip[dry])
  
  # Onto extreme wet days
  # Calc current percent rainfall in 3 highest wet days
  current_high_vol <- sum(rev(sort(annual_precip[wet]))[1:3])
  high_vol_cutoff <- rev(sort(annual_precip[wet]))[3]
  # Set highflow increase to be a percentage increase from original value. 
  final_high_vol <- current_high_vol + (highprecip_perc * current_high_vol) 
  high_diff <- final_high_vol - current_high_vol

  high_days_locs <- which(annual_precip[wet] >= high_vol_cutoff)
  wet_days_locs <- which(annual_precip[wet]>0 & annual_precip[wet]<high_vol_cutoff)
  
  # If there is enough water from dry harvest for high day goal, add amt needed and 
  # distribute rest across wet season precip days
  if(high_diff <= dry_harvest){
    annual_precip[wet][high_days_locs] <- annual_precip[wet][high_days_locs] + high_diff/length(high_days_locs)
    remaining_harvest <- dry_harvest - high_diff
    wet_days_locs <- which(annual_precip[wet]>0 & annual_precip[wet]<high_vol_cutoff)
    if(exists("wet_days_locs") == TRUE){
      annual_precip[wet][wet_days_locs] <- annual_precip[wet][wet_days_locs] + remaining_harvest/length(wet_days_locs)
    } 
    else{
      print(remaining_harvest)
    }
    
  } else{
    # Otherwise if dry harvest is not enough to fill high days deficit, shave some additional precip off wet season days
    remaining_deficit <- high_diff - dry_harvest
    # Shave off precip from wet season days to make up high day deficit
    annual_precip[wet][wet_days_locs] <- annual_precip[wet][wet_days_locs] - remaining_deficit/length(wet_days_locs)
    # Add deficit to high precip days
    annual_precip[wet][high_days_locs] <- annual_precip[wet][high_days_locs] + (dry_harvest+remaining_deficit)/length(high_days_locs)
  }
  return(annual_precip)
}

interannual_precip_manip <- function(merced_grids, run_parameters){
  # Function for modifying precip intensity across all years, input is entire collection of timeseries
  # intensity parameters
  orig_perc_low <- unlist(run_parameters[[1]]["orig_perc_low"]) # val 0-1, avg annual precip value low before shifting precip across years 
  orig_perc_high <- unlist(run_parameters[[1]]["orig_perc_high"]) # val 0-1, avg annual precip value high before shifting precip across years 
  final_perc_low <- unlist(run_parameters[[1]]["final_perc_low"]) # val 0-1, avg annual precip value low before shifting precip across years. Must be lower than orig. 
  final_perc_high <- unlist(run_parameters[[1]]["final_perc_high"]) # val 0-1, avg annual precip value high before shifting precip across years. Must be higher than orig.
  extreme_shift_low <- as.numeric(unlist(run_parameters[[1]]["extreme_shift_low"])) # val -(0-1), reduce driest years this far below current low
  extreme_shift_high <- as.numeric(unlist(run_parameters[[1]]["extreme_shift_high"])) # val 0-1, raise highest years this far above current high
  extreme_shift_percent <- as.numeric(unlist(run_parameters[[1]]["extreme_shift_percent"])) # val 0-1, number of years corresponding to this percentage will be
  # shifted out to new extremes on min and max
  # To achieve metric in Persad paper, increase occurrence of years in 20th/80th percentage
  # of precip to get an increased frequency of years in these extreme bins. 
  
  # Separate each grid into a 64-yr timeseries (list of 64 lists)
  updated_merced_grids <- merced_grids
  # within 64-yr timeseries for each grid: 
  for(grid_num in seq(1:length(merced_grids))){
    grid <- merced_grids[[grid_num]]
    
    # assign all years their percentile based on cumsum of precip
    cumsums <- unlist(lapply(grid, sum))
    # Move dry years from this (higher) percentile val down to final percentile val (e.g., 20th perc)
    orig_dry_threshold <- quantile(cumsums, orig_perc_low)
    # Final target to move dry vals down to. Eg., 20th percentile. 
    new_dry_threshold <- quantile(cumsums, final_perc_low)
    # total precip volume to remove from all years in lower-down percentile
    reduction_volume <- orig_dry_threshold-new_dry_threshold
    # target certain number of dry years to remove precip from
    dry_years_locs <- which(cumsums <= orig_dry_threshold & cumsums >= new_dry_threshold)
    # harvest precip proportionally off all flow days in dry years
    for(dry_year in dry_years_locs){
      reduction_perc <- reduction_volume/sum(grid[[dry_year]])
      grid[[dry_year]] <- grid[[dry_year]]*(1-reduction_perc)
    }
    # Tally up extreme dry years 
    low_days_count <- round(length(grid)*extreme_shift_percent)
    # find low diff, value to subract off lowest current days to bring it x% lower than historic
    low_diff <- min(cumsums)*extreme_shift_low
    low_thresh <- sort(cumsums)[low_days_count]
    extreme_low_locs <- which(cumsums <= low_thresh)
    # subtract the low diff from x lowest years in record so they all move toward new dry extreme
    for(year in extreme_low_locs){
      reduction_perc <- low_diff/sum(grid[[year]])
      grid[[year]] <- grid[[year]]*(1-reduction_perc)
    }
    extreme_dry_harvest <- low_diff * low_days_count
    
    # tally total amt of dry year precip harvest
    precip_harvest <- reduction_volume*length(dry_years_locs) + extreme_dry_harvest
    # Calc amt of precip needed to fulfill changes, add water from dry harvest first, and 
    # if more needed add from middle-ground years
    
    # target wet years to add precip to, split precip harvest among these years
    # orig wet thresh: a value lower than final wet thresh (making wet season wetter)
    orig_wet_threshold <- quantile(cumsums, orig_perc_high)
    final_wet_threshold <- quantile(cumsums, final_perc_high)
    addition_volume <- final_wet_threshold - orig_wet_threshold
    wet_year_locs <- which(cumsums >= orig_wet_threshold & cumsums <= final_wet_threshold)
    total_wet_addition <- length(wet_year_locs) * addition_volume
    
    # Add to each year in percentile category based on total percent increase
    for(wet_year in wet_year_locs) {
      perc_increase <- (sum(grid[[wet_year]]) + addition_volume)/sum(grid[[wet_year]])
      grid[[wet_year]] <- grid[[wet_year]]*perc_increase
    }
    
    # Extreme wet years
    high_days_count <- round(length(grid)*extreme_shift_percent)
    # find high diff, value to add onto highest current days to bring it x% above historic
    high_diff <- max(cumsums)*extreme_shift_high
    high_thresh <- min(tail(sort(cumsums), high_days_count))
    # Add the high diff to the x highest years in record so they all move toward new wet extreme
    extreme_high_locs <- which(cumsums >= high_thresh)
    for(year in extreme_high_locs){
      perc_increase <- (sum(grid[[year]]) + high_diff)/sum(grid[[year]])
      grid[[year]] <- grid[[year]]*(perc_increase)
    }

    extreme_wet_addition <- high_diff * high_days_count
    
    # Figure out how much the wet year additions exceed dry harvest
    total_wet_take <- total_wet_addition + extreme_wet_addition
    remaining_take <- total_wet_take - precip_harvest
    if(remaining_take[[1]] <= 0){
      
    } else {
      # For remaining surplus of wet addition, get there from taking flow off middle years
      take_each_year <- remaining_take/10 # pick a number?
      # define middle years, by rank order of 10 middle years
      middle_years <- seq(28, 37, by=1)
      middle_years_low <- sort(cumsums)[min(middle_years)]
      middle_years_high <- sort(cumsums)[max(middle_years)]
      middle_years_loc <- which(cumsums >= middle_years_low & cumsums <= middle_years_high)
      # remove take each year from each using multiply by percent method
      for(year in middle_years_loc){
        reduction_perc <- take_each_year/sum(grid[[year]])
        grid[[year]] <- grid[[year]]*(1-reduction_perc)
      }
    }
    updated_merced_grids[[grid_num]] <- grid
  }
  # Return updated Merced grids
  return(updated_merced_grids)
}

#################
##### MAIN ######
#################

# Load run parameters
for(run_number in 1:19){
  print(paste("run number", run_number))
  run_parameters <- set_run_parameters(run_number)
  
  # Set path to location of input data
  loc_path = "/data_inputs/detrended-one-16th-rdata/"
  filenames = list.files(path = paste(getwd(), loc_path, sep=""), pattern="*.rds")
  filepaths = lapply(filenames, function(x) paste(getwd(), loc_path, x, sep=""))
  files = lapply(filepaths, readRDS)
  # File organization: 64 files, each for a year of data from 1950-2013. Leap years included, so every forth file is larger.
  # Within a file, included is every day of data for each grid in the state. Grids are rep'd as points,
  # 4868 grids/points total. Loc, date, precip, and temp (as min and max) are included in each row. 
  # I remove precip column for processing. Data is organized by listing the first day of year's data
  # for every grid, then moving to the next date and the next. So to pull out a timeseries for a single 
  # grid, pull out every 4868th data point.
  
  # Pull out only the grids corresponding to Merced Basin for calculations
  merced_output <- list_merced_indices(files)
  merced_indices <- merced_output[[1]]
  merced_grids <- merced_output[[2]]
  
  # apply interannual (across years) changes before entering into loop. Result is in grid format
  # instead of original data format. 
  updated_merced_grids <- interannual_precip_manip(merced_grids, run_parameters)
  updated_files <- list()
  # Perform intraannual changes for all 70 years on updated files (within-year)
  # Loop through years (64)
  for(current_year in seq(1, length(files))){ 
    # compile all timeseries for the given year (100 across all Merced grids)
    merced_grids_current_year <- list()
    
    # Update current year file with updated merced grids
    file_to_update <- files[[current_year]]
    
    for(current_grid in seq(1, length(updated_merced_grids))){
      # current_grid is the merced grid (out of 100), current_year is the current year (out of 64)
      merced_grids_current_year <- updated_merced_grids[[current_grid]][current_year]
      # next: apply an intensity alteration to the given year and grid
      new_grids = lapply(merced_grids_current_year, intra_precip_manip, run_parameters)
      new_grids = lapply(new_grids, unlist)
  
      locs = seq(merced_indices[[current_grid]], length(files[[1]][,1]), 4868) 
      # update file with the updated precip for the given grid and year.
      file_to_update[,6][c(locs)] <- new_grids[[1]]
    }

    updated_files <- append(updated_files, list(file_to_update))
  }
  
  # Convert updated files into grid-based .txt files, and combine year-separated files into single large files for each grid,
  # for input to hydrologic model. 
  grid_format <- list_grids_merced(updated_files, merced_indices)
  backup_grid_format <- grid_format
  
  # Add six years of average data to beginning of dataset to give model a warm-up period. These years will be removed from
  # final results. Dataset now has 70 years of data until the 6 warm-up years are removed. 
  grid_format <- add_warmup_years(grid_format)
  
  output_path = paste(getwd(), "/data_outputs/detrended-one-16th-rdata/txtformat_run",run_number,"/",sep="")
  dir.create(output_path, showWarnings = FALSE)
  for(index in seq(1, length(merced_indices))){
    grid_format[[index]] <- do.call(rbind, grid_format[[index]])
    lat <- toString(round(grid_format[[index]][,"lat"][1], 4))
    lon <- toString(round(grid_format[[index]][,"lon"][1], 4))
    output <- grid_format[[index]][,3:7]
    write.table(output, file=paste(output_path,"data_", lat,"_", lon, ".txt", sep=""), sep="\t", row.names=F, col.names=FALSE)
  }
  
}
