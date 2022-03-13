import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/SearchButton';
import QEButton from './components/QueryExpansionButton';
import SearchField from './components/search';
import UseSwitchesCustom from './components/toggle';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options'
import Box from '@mui/material/Box';
import research_logo from './logos/Re-Search-logos_transparent.png';

import Switch from '@mui/material/Switch';
import SwipeableTemporaryDrawer from './components/advancedOptions';

// TODO: npm audit fix --force (takes some time tho)

function App() {

  const [search, setSearch] = React.useState('');
  const [json, setJson] = React.useState({Results:[]});
  const label = { inputProps: { 'aria-label': 'Switch demo' } };
  const [values,setValues] = React.useState({
    oldest: false,
    latest: false,
    featured: true,
    authors: true,
    author_text:'',
    range_from:null,
    range_to: null
  })

  function getOptions(optval){
    setValues(optval);
    // console.log(values);

  }

  function Search() {
    return fetch('http://127.0.0.1:5000/' + search).then(response => response.json()).then(data => {
      console.log(data);

      setJson(data);
      console.log(json);
    });
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
    return authors    
  }


  function QueryExpansion() {
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
        width : '50%'
      }}>
        <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
        />

      </div>
      <SwipeableTemporaryDrawer parentCallback={getOptions}/>
      <ButtonGroup variant="contained" aria-label="outlined primary button group">
      <SearchButton parentCallback={Search} />
      <QEButton parentCallback={QueryExpansion} />
      </ButtonGroup>
      <div>
        {json.Results.map(curr_element => {
          let std_date = standardize_dates(curr_element.date);

            return <Box
            padding={1}
           // if statements: one for modile devices, one for all desktops. 
           >
             <p>
               <p><font COLOR="grey" SIZE="2" face="Arial">{curr_element.url}</font></p>
               <a href={curr_element.url}><font COLOR="green" SIZE="5" face="Arial">{curr_element.title}</font></a>
               <p><font COLOR="grey" face="Arial">{std_date}</font></p>
               <p><font face="Arial">{abstractgenerator(curr_element.description)}</font></p>
               <p><font face="Arial">{authorlist(curr_element.authors)}</font></p>
             </p></Box>;
         })} 
      </div>
    </div>
  )

}


export default App;