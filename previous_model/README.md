# NBA_pred
Creates a 'growable' NBA dataset using public team data (traditional, opponent, and miscellaneous) from basketball reference and develop a neural network using keras sequential dense layers to predict the outcomes of NBA games. <br/>
Use both home and away team stats and respective scores in the past to train the model. The prediction is done from the most recent data. 
Ridge regression average accuracy 63%, neural network average accuracy 62%. <br/>
To run the model, download all directories and run pred_model.py, then follow the instruction to enter full team names. The dataset is updated biweekly to account for more recent games. <br/>
For new season, update the YEAR in each python file to the new season year (i.e., for the 2019-2020 season, change YEAR to 2020)

![sample](https://github.com/k-shen/NBA_pred/blob/master/sample_output.png)
