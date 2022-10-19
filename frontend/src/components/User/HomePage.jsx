import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
// import MenuIcon from "@mui/icons-material/Menu";

export default function HomePage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState("Logged in");
  const [tweetData, setTweetData] = useState([]);

  let token = localStorage.getItem("token");

  useEffect(() => {
    if (status == "Logged in") {
      fetch(`http://localhost:8080/twitter/home_timeline`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        }
      })
        .then((resp) => resp.json())
        .then((data) => {
          console.log(data["details"]);
          setStatus("Successfully fetched data");
        //   setTweetData(data["details"]);
        //   console.log(tweetData);

          var result = JSON.parse(JSON.stringify(data["details"]));
          setTweetData(result);
          console.log(result);
        });
    }
  }, []);

  useEffect(() => {
    if (token === null || token === undefined) {
      navigate("/twitter/login");
    }
  }, []);

  // Logout the user
  const logoutUser = () => {
    localStorage.removeItem("token");
    navigate("/twitter/login");
  };

  return (
    <div>
      <Box sx={{ width:1450, flexGrow: 1, position:"fixed"}}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
              Twitter
            </Typography>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              User Home
            </Typography>
            <Button onClick={logoutUser} color="inherit">
              Logout
            </Button>
          </Toolbar>
        </AppBar>
      </Box>
      <div className="container-hs">
        <br></br>
        <br></br>
        <br></br>
        <br></br>
        {tweetData.map((tweet,i) => {
            return(
                <div key ={i}>
                    <div className="container-div">
                        <h5>Tweet@{tweetData[i]["tweeter_id"]}</h5>
                        <h5>Tweet : {tweetData[i]["tweet"]}</h5>
                        <div>
                            <div className="container-activity">
                                <h5>Tweeted By : {tweetData[i]["tweeted_by"]}</h5>
                                <h5>Tweet ID : {tweetData[i]["tweet_id"]}</h5>
                            </div>
                            <div className="container-activity">
                                <h5 className="activity">Likes : {tweetData[i]["likes_count"]}</h5>
                                <h5 className="activity">Retweets : {tweetData[i]["retweets_count"]}</h5>
                                <h5 className="activity">Replies : {tweetData[i]["replies_count"]}</h5>
                            </div>
                        </div>
                        
                    </div>
                </div>
            );
        })}
      </div>
    </div>
  );
}
