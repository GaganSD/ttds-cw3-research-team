import logo from './logo.svg';
import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/serachbutton';
import SearchField from './components/search';
import UseSwitchesCustom from './components/toggle';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options'
import Box from '@mui/material/Box';
import research_logo from './logos/Re-Search-logos_transparent.png';

import Switch from '@mui/material/Switch';
import SwipeableTemporaryDrawer from './components/advancedOptions';


function App() {

  const [search, setSearch] = React.useState('');
  const [json, setJson] = React.useState({Results:[]});
  const label = { inputProps: { 'aria-label': 'Switch demo' } };

  function Search() {
    return fetch('http://127.0.0.1:5000/' + search).then(response => response.json()).then(data => {
      console.log(data);
      setJson(data);
      console.log(json);
    });
  }

  function BasicSwitches() {
    return (
      <div>
        <Switch {...label} defaultChecked />
        <Switch {...label} />
        <Switch {...label} disabled defaultChecked />
        <Switch {...label} disabled />
      </div>
    );
  }
  
  function TextEntered(searchval) {
    setSearch(searchval);
  }

  function standardize_dates(string_date) {
    string_date=string_date.replaceAll('-','/');
    string_date = string_date.replace(/\s+/g,"");

    var _format="d/m/y"
    var formatItems=_format.split('/');
    var dateItems=string_date.split('/');
    var dayIndex=formatItems.indexOf("d");
    var monthIndex=formatItems.indexOf("m");
    var yearIndex=formatItems.indexOf("y");
    var yr = parseInt(dateItems[yearIndex]);
    if (yr<100 && yr<=21){ //handling 2 digit years
        var year="20"+yr;
    }
    else if (yr<100){
        var year="19"+yr;
    }
    else{
      var year = yr;
    }

    if (isNaN(dateItems[monthIndex])){ //in case the month is written as a word
      var d = new Date(string_date);
    }
    else {
      var month=parseInt(dateItems[monthIndex]);
      month-=1;
      var d = new Date(year,month,dateItems[dayIndex]);
    }

    let formatted = [String ("0" + d.getDate()).slice(-2), String ("0" + (d.getMonth() +1)).slice(-2), d.getFullYear()].join('/');

    return formatted;
  }
  // todo: test in phone.
  var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  function abstractgenerator(text){
    if (text!=""){
      if (isMobile){
        return text.substring(0,100)+"..."
      }
      else{
        return text.substring(0,500)+"..."
      }
    }
  }

  function authorlist(authors){
    var lower=authors.toLowerCase()
    if (authors.includes(",")){
      return "Authors: "+ authors
    }
    else if (!(lower=="n/a" || lower=="na" || lower=="n-a" || lower=="")){
      return "Author: "+ authors
    }
  }


  return (
    <div className="App" style={{
      // width: '100%',
      marginLeft: '5em',
      marginRight: '5em'
    }}>
    <div className="toggle_switch" float="center" id="toggle_switch">
      {/* display='flex' justifyContent="flex-end"  
      tried:
      flaot:right
      */}
    </div>

    <img src={research_logo} width="300em" height="150em"/>
    <UseSwitchesCustom  float="right" parentCallback={BasicSwitches} />
      <div className='SearchOptions' style={{
      }}>
        <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
        />
        <div className='Options'>
          <Options />
        </div>
      </div>
      <SearchButton parentCallback={Search} />
      <div>
        {json.Results.map((name, key) => {
          
          let std_date = standardize_dates(name.date);

          return <Box
           padding={1}
          // if statements: one for modile devices, one for all desktops. 
          >
            <p key={key}>
              <p><font COLOR="grey" SIZE="2" face="Arial">{name.url}</font></p>
              <a href={name.url}><font COLOR="green" SIZE="5" face="Arial">{name.title}</font></a>
              <p><font COLOR="grey" face="Arial">{std_date}</font></p>
              <p><font face="Arial">{abstractgenerator(name.description)}</font></p>
              <p><font face="Arial">{authorlist(name.authors)}</font></p>
            </p></Box>;
        })}
      </div>
      <SwipeableTemporaryDrawer/>
    </div>
  )

}


export default App;