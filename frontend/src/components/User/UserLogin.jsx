import React, { useState } from "react";
import { useNavigate } from "react-router";

export default function UserLogin({ setToken }) {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({
    email: "",
    password: "",
  });
  const [jwtToken, setjwtToken] = useState("");
  const [message, setMessage] = useState();
  const [isLogin, setIsLogin] = useState(false);
  const [redirect, setRedirect] = useState(null);

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value,
    });
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    loginUser(credentials)
      .then((data) => {
        setToken(data.access_token);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const navigateHome = () => {
    navigate("/twitter/home");
  };

  const loginUser = (credentials) => {
    return fetch("http://localhost:8080/twitter/login?account_handle or email="
    .concat(credentials.email).concat("&password=").concat(credentials.password), {
      method: "POST",
    })
      .then((resp) => resp.json())
      .then((data) => {
        console.log(data);
        if (data.message === "Password is incorrect") {
          setjwtToken("");
          setIsLogin(false);
          setMessage("Invalid login");
        } else {
          if (data.access_token === undefined) {
            setjwtToken(data.access_token);
            setIsLogin(false);
            setMessage("Invalid login");
          } else {
            localStorage.setItem("token", data.access_token);
            setjwtToken(data.access_token);
            setIsLogin(true);
            setMessage("Your logged in with Authentication token ");
            setRedirect("/twitter/home");
            navigateHome();
          }
        }
      });
  };
  return (
    <div className="form">
      <form onSubmit={handleSubmit}>
        <label className="label">Username:</label>
        <input
          type="text"
          name="email"
          value={credentials.email}
          onChange={handleChange}
          className="input"
        />
        <label>Password:</label>
        <input
          type="password"
          name="password"
          value={credentials.password}
          onChange={handleChange}
          className="input"
        />
        <br />
        <button type="submit" className="button">
          Login
        </button>
      </form>
    </div>
  );
}