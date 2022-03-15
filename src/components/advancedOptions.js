import * as React from 'react';
import Box from '@mui/material/Box';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox'
import TextField from '@mui/material/TextField';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import Stack from '@mui/material/Stack';
import DesktopDatePicker from '@mui/lab/DesktopDatePicker';
import { SliderValueLabelUnstyled } from '@mui/base';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';



export default function SwipeableTemporaryDrawer(props) {
  const [state, setState] = React.useState({
    top: false,
    left: false,
    bottom: false,
    right: false,
  });

  // let valcopy = {
  //   sort_by: "Featured",
  //   authors: true,
  //   author_text:'',
  //   range_from:null,
  //   range_to: null
  // };

  const [fromDate, setFromDate] = React.useState(null);
  const [toDate, setToDate] = React.useState(null);
  const [author_text, setAuthorText] = React.useState("");
  const [radio_choice, setRadioChoice] = React.useState("Featured");


  React.useEffect(() => {
    console.log(fromDate);
    props.parentCallback("date_from", fromDate);
  }, [fromDate]);


  React.useEffect(() => {
    console.log(toDate);
    props.parentCallback("date_to", toDate);
  }, [toDate]);

  React.useEffect(() => {
    console.log(author_text);
    props.parentCallback("author", author_text);
  }, [author_text]);

  React.useEffect(() => {
    console.log(radio_choice);
    props.parentCallback("sort_by", radio_choice);
  }, [radio_choice]);
  const handleChange = (e) => {
    let eventtype;
    try{
      eventtype = e.target.type;
    }
    catch{
      eventtype = "date";
    }
    if(eventtype === "radio"){
      setRadioChoice(e.target.value);
    }
    else if(eventtype === "text"){
      if(e.target.value !== ''){
         setAuthorText(e.target.value);
      }

    }
    console.log(radio_choice);
    console.log(toDate);
  };

  const toggleDrawer = (anchor, open) => (event) => {
    if (
      event &&
      event.type === 'keydown' &&
      (event.key === 'Tab' || event.key === 'Shift')
    ) {
      return;
    }

    setState({ ...state, [anchor]: open });
  };

  const list = (anchor) => (
    <Box
      sx={{ width: anchor === 'top' || anchor === 'bottom' ? 'auto' : 250 }}
      role="presentation"
      // onClick={toggleDrawer(anchor, false)}
      // onKeyDown={toggleDrawer(anchor, false)}
    >

      <Divider />

      <List>


        <FormControl>
            <FormLabel id="sortby">Algorithm:</FormLabel>
            <RadioGroup
              aria-labelledby='sortbybuttons'
              defaultValue= {radio_choice}
              name = "radio buttons"
              onChange={handleChange}>

                <FormControlLabel control={<Radio/>}  label="Approximate NN" value="Approximate NN" />
                <FormControlLabel control={<Radio/>} label="BM25" value="BM25"/>
                <FormControlLabel control={<Radio/>}  label="TF-IDF" value="TF-IDF"/>

              </RadioGroup>
        </FormControl>

      </List>

      <Divider/>

      <List>

        <ListItem button key={"Authors:"}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"Authors:"} />
        </ListItem>

        <TextField defaultValue = {author_text} onChange = {handleChange} id="outlined-basic" label="Authors" variant="outlined"/>

        <ListItem button key={"Range:"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Range:"} />
        </ListItem>


        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Stack spacing={3}>
            <DesktopDatePicker
            label="From"
            inputFormat="MM/dd/yyyy"
            value={fromDate}
            onChange={(newfromvalue) => {
              setFromDate(newfromvalue);
              handleChange();
              // console.log(fromDate);
            }}
            renderInput={(params) => <TextField {...params} />}
            />
            <DesktopDatePicker
            label="To"
            inputFormat="MM/dd/yyyy"
            value={toDate}
            onChange={(newtovalue) => {
              setToDate(newtovalue);
              handleChange();
              // console.log(toDate);
            }}
            renderInput={(params) => <TextField {...params} />}
            /> 
          </Stack>
        </LocalizationProvider>

      </List>

      <Divider />

{/* 
      <List>
        {['Sort By:', 'Trash', 'Spam'].map((text, index) => (
          <ListItem button key={text}>
            <ListItemIcon>
              {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
            </ListItemIcon>
            <ListItemText primary={text} />
          </ListItem>
        ))}
      </List> */}
    </Box>
  );

  return (
    <div>
      {['Advanced Search Options'].map((anchor) => (
        <React.Fragment key={"left"}>
          <Button onClick={toggleDrawer("left", true)}>{anchor}</Button>
          <SwipeableDrawer
            anchor={"left"}
            open={state["left"]}
            onClose={toggleDrawer("left", false)}
            onOpen={toggleDrawer("left", true)}
          >
            {list("left")}
          </SwipeableDrawer>
        </React.Fragment>
      ))}
    </div>
  );
}
