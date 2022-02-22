import logo from './logo.svg';
import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import FilterButton from './components/filterbutton';
import SearchField from './components/search';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import SearchButton from './components/serachbutton';



function App() {
  return (
    <div className="App">
      <Typography variant='h1' gutterBottom>
        ReSearch
      </Typography>
      <div className='SearchOptions'>
        <FilterButton/>
        <SearchField/>
      </div>
      <SearchButton/>
    </div>
  );
}

export default App;