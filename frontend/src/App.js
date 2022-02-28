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
  return (
    <div className="App">
      <div className="Logo">
        <Typography variant='h1' gutterbottom>
          ReSearch
        </Typography>
      </div>
      <div className='SearchOptions'>
        <SearchField/>
        <Options/>
      </div>
      <SearchButton/>
    </div>
  );
}

export default App;