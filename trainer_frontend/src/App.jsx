import "./App.css";
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import TrainWithPartner from "./views/TrainWithPartner/TrainWithPartner.jsx";
import Home from "./views/Home/Home.jsx";
import ChooseExercise from "./views/ChooseExercises/ChooseExercise.jsx";
import TrainingHistory from "./views/TrainingHistory/TrainingHistory.jsx";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />}/>
                <Route path="/train/:exercise" element={<TrainWithPartner/>}/>
                <Route path="/choose/exercise" element={<ChooseExercise />}/>
                <Route path="/history" element={<TrainingHistory />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;