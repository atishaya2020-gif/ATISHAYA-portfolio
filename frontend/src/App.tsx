import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AnalyticsTracker } from "./components/AnalyticsTracker";
import { Navbar } from "./components/navigation/Navbar";
import { About } from "./pages/About";
import { Contact } from "./pages/Contact";
import { Home } from "./pages/Home";
import { ProjectDetail } from "./pages/ProjectDetail";
import { Projects } from "./pages/Projects";
import { Stack } from "./pages/Stack";

function App() {
  return (
    <BrowserRouter>
      <AnalyticsTracker />
      <div className="min-h-screen bg-near-black text-white">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:slug" element={<ProjectDetail />} />
            <Route path="/stack" element={<Stack />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
