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

// TODO: npm audit fix --force (takes some time tho)

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
      <SwipeableTemporaryDrawer/>
      <SearchButton parentCallback={Search} />
      <div>
        {json.Results.map((name, key) => {
            return <Box bgcolor="#E8E8E8"
            //  display="flex" //probably dont need this anymore but keeping it here just in case...
            //  sx={{ overflow: 'auto' }}
            //  sx={{ width: '50%' }}
            //  style={{justifyContent: "center"}}
            //  style={{alignItems: "center"}}
            //  style={{position: "relative"}}
              marginTop={1}
              padding={2}
            >
              <p key={key}>
                <p><font COLOR="grey" SIZE="2" face="Arial">{name.url}</font></p>
                <a href={name.url}><font COLOR="green" SIZE="5" face="Arial">{name.title}</font></a>
                <p><font COLOR="grey" face="Arial">{name.date}</font></p>
                <p><font face="Arial">{name.description}</font></p>
                <p><font face="Arial">Author(s): {name.authors}</font></p>
              </p></Box>;
          
        })}
      </div>
    </div>
  )

}


export default App;