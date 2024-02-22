import React from 'react';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import LoginPage from './LoginPage';
import ChatPage from './ChatPage';

export type UserInfo = {
  id: number,
  name: string,
  password: string,
  description: string,
}

export type AppState = {
  currentPage: string,
  currentUser: UserInfo|null,
  appState: string,
}

export type StateProps = {
    state: AppState,
    setState: React.Dispatch<React.SetStateAction<AppState>>
}    

function App() {
  let [state, setState] = React.useState<AppState>({
    currentPage: "home", 
    currentUser: null,
    appState: "init"
  });

  let renderPage;
  if (state.currentPage === "home") {
    renderPage = <LoginPage state={state} setState={setState}/>
  } else if (state.currentPage === "chat") {
    renderPage = <ChatPage state={state} setState={setState}/>
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
