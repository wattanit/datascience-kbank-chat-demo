import React from 'react';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import LoginPage from './LoginPage';
import ChatPage from './ChatPage';

type AppState = {
  currentPage: string;
}

function App() {
  let [state, setState] = React.useState<AppState>({currentPage: "chat"});

  let renderPage;
  if (state.currentPage === "home") {
    renderPage = <LoginPage/>
  } else if (state.currentPage === "chat") {
    renderPage = <ChatPage/>
  }else {
    renderPage = <div>Not Found</div>
  } 

  return (
    <div className="App">
      <Header/>
      <header className="App-header">
        {renderPage}
      </header>
      <Footer/>
    </div>
  );
}

export default App;
