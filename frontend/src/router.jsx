import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import UserLogin from "./components/User/UserLogin";
import HomePage from "./components/User/HomePage";

const Router = () => {
  return (
    <div>
      <BrowserRouter>
        <Routes>
          <Route exact path="/" element={<App />} />
          <Route exact path="/twitter/login" element={<UserLogin />} />
          <Route exact path="/twitter/home" element={<HomePage />} />
         
        </Routes>
      </BrowserRouter>
    </div>
  );
};

export default Router;