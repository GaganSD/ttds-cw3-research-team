import logo from './logo.svg';
import './App.css';

import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/serachbutton';
import SearchField from './components/search';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options';

import ResultsList from './ResultList'
import React, { Component } from 'react'



class App extends Component {
  render(){
    return (
      <div className='App'>
      <div className='Logo'>
        <Typography variant='h1' gutterbottom>
          ReSearch
        </Typography>
      </div>
      <div className='SearchOptions'>
        <SearchField/>
        <div className='Options'>
          <Options/>
        </div>
      </div>
      <SearchButton/>
      <ResultsList />
    </div>
    )
  }
}

export default App;