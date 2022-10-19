
import './App.css';
import {useNavigate} from "react-router-dom";
import React, { useState, useEffect } from "react";

function App() {
  const navigate = useNavigate();

  const navigateUserLogin = () => {
    navigate("/twitter/login");
  };
  const navigateUserSignup = () => {
    navigate("/twitter/register");
  };
  return (
    <div className="App">
      <h3 className="txt">Twitter</h3>
      <br />
      <br />
      <div>
        <div className="btn">
          <button className="btn-primary m-2" onClick={navigateUserLogin}>
            User Login
          </button>
          <button className="btn-primary m-2" onClick={navigateUserSignup}>
            User Signup
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
