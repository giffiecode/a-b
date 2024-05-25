total_points = 1000 
eliminate = 0 

num_players = 5 
# adjust num_of_round 
num_of_round = 10  
# adjust to play with buy interest with respect to the buy limit at each round 
round_buy_ratio <- c(0.9, 0.8)  

buy_limit_func <- function(num_players) {
  # the approximate number of round. go up: buy less than the limit. go down: more people join 
  buy_limit <- (total_points / num_players) / num_of_round
  return(buy_limit)
}  

buy_limit <- buy_limit_func(num_players) 


# total points purchased   
round_total_purchases <- sapply(round_buy_ratio, function(ratio) {
  ratio * num_players * buy_limit
}) 

eliminate_rate <- 0.5   

# total points eliminated 
round_total_eliminate <- eliminate_rate * round_total_purchases   

# alpha is the purchase price adjustment param   
alpha = 1.2 
# purchase price function 
price_of_b <- total_points / (total_points - sum(round_total_eliminate)) * alpha 