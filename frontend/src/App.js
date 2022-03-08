import logo from './logo.svg';
import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/serachbutton';
import SearchField from './components/search';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options'



function App() {

  const [search, setSearch] = React.useState('');
 

  function Search() {
    alert(search);
  }

  function TextEntered(searchval){
      setSearch(searchval);
  }



  return (
    <div className="App">
      <div className="Logo">
        <Typography variant='h1' gutterbottom>
          ReSearchEd
        </Typography>
      </div>
      <div className='SearchOptions'>
        <SearchField parentCallback = {TextEntered}/>
        <div className='Options'>
          <Options/>
        </div>
      </div>
      <SearchButton parentCallback = {Search}/>
    </div>
  );
}

export default App;