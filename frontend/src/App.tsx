import React from "react";
import { LandingPage } from "./pages/LandingPage";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { OverviewPage } from "./pages/OverviewPage";
import { LoadingSpinner } from "./components/LoadingSpinner";

export const App = React.memo(() => {
  const [lendeeName, setLendeeName] = React.useState<string | undefined>(
    undefined
  );
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <LandingPage
              lendeeName={lendeeName}
              setLendeeName={setLendeeName}
            />
          }
        />
        <Route
          path="/overview"
          element={
            lendeeName != null ? (
              <OverviewPage lendeeName={lendeeName} />
            ) : (
              <LoadingSpinner />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
});
