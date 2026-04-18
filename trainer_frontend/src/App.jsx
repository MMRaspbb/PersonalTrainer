import "./App.css";
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import TrainWithPartner from "./views/TrainWithPartner/TrainWithPartner.jsx";
import Home from "./views/Home/Home.jsx";
import ChooseExercise from "./views/ChooseExercises/ChooseExercise.jsx";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />}/>
                <Route path="/train/:exercise" element={<TrainWithPartner/>}/>
                <Route path="/choose/exercise" element={<ChooseExercise />}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;