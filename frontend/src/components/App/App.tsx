import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Provider } from "react-redux";
import { store } from "../../store/store.ts";
import HomePage from "../../pages/HomePage.tsx";

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    </Provider>
  );
};

export default App;
