import "./App.css";
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import TrainWithPartner from "./views/TrainWithPartner/TrainWithPartner.jsx";
import Home from "./views/Home/Home.jsx";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/train" element={<TrainWithPartner/>}/>
                <Route path="/home" element={<Home />}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;