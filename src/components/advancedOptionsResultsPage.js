
import * as React from 'react';
import Box from '@mui/material/Box';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import FormControlLabel from '@mui/material/FormControlLabel';
import TextField from '@mui/material/TextField';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import Stack from '@mui/material/Stack';
import DesktopDatePicker from '@mui/lab/DesktopDatePicker';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import HelpDialog from "./helpdialog";
import { useParams } from 'react-router-dom'


import 'typeface-roboto';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

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
    const { query, df, dt, alg, srchtyp, ds, pn } = useParams();
    const theme = createTheme({
        components: {
            MuiTypography: {
                defaultProps: {
                    variantMapping: {
                        h1: 'h2',
                        h2: 'h2',
                        h3: 'h2',
                        h4: 'h2',
                        h5: 'h2',
                        h6: 'h2',
                        subtitle1: 'h2',
                        subtitle2: 'h2',
                        body1: 'span',
                        body2: 'span',
                    },
                },
            },
        },
    });


    const [fromDate, setFromDate] = React.useState(new Date(df));
    const [toDate, setToDate] = React.useState(new Date(dt));
    const [radio_choice_algorithm, setRadioChoiceAlgorithm] = React.useState(alg);
    const [radio_choice_searchtype, setRadioChoiceSearchType] = React.useState(srchtyp);


    React.useEffect(() => {
        console.log(fromDate);
        props.parentCallback("date_from", fromDate);
    }, [fromDate]);


    React.useEffect(() => {
        console.log(toDate);
        props.parentCallback("date_to", toDate);
    }, [toDate]);



    React.useEffect(() => {
        console.log(radio_choice_algorithm);
        props.parentCallback("algorithms", radio_choice_algorithm);
    }, [radio_choice_algorithm]);

    React.useEffect(() => {
        console.log(radio_choice_searchtype)
        props.parentCallback("searchtype", radio_choice_searchtype)
    }, [radio_choice_searchtype]);

    const handleChange = (e) => {
        let eventtype;
        try {
            eventtype = e.target.type;
        }
        catch {
            eventtype = "date";
        }
        if (eventtype === "radio") {
            console.log(props.datasets);
            if (e.target.name === "algorithmbuttons") {
                setRadioChoiceAlgorithm(e.target.value);
            }
            else {
                setRadioChoiceSearchType(e.target.value);
            }
        }


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
            sx={{ width: anchor === 'top' || anchor === 'bottom' ? 'auto' : 400 }}
            role="presentation"
        >
            <div style={{
                display: "flex",
                justifyContent: "center"
            }}>
                <h2><b> Advanced Options</b></h2>
                <div style={{
                    marginTop: "1em",
                    marginLeft: "1em"
                }}>
                    <HelpDialog />
                </div>
            </div>
            <Divider />

            <List>


                <FormControl sx={{
                    margin: 2
                }}>
                <FormLabel id="sortby">✨ Ranking Algorithm:</FormLabel>
                    <RadioGroup
                        aria-labelledby='algorithmbuttons'
                        defaultValue={radio_choice_algorithm}
                        name="algorithmbuttons"
                        onChange={handleChange}>

                        <FormControlLabel control={<Radio />} label="TF-IDF" value="TF_IDF" />
                        <FormControlLabel control={<Radio />} label="BM25" value="BM25" />
                        <FormControlLabel control={<Radio />} label="Transformers & Nearest Neighbors" value="APPROX_NN" />

                    </RadioGroup>
                </FormControl>

            </List>

            <Divider />

            <List>
                <FormControl sx={{
                    margin: 2
                }}>
            <FormLabel id="sortby">🔎 Search Type:</FormLabel>
                    <RadioGroup
                        aria-labelledby='searchtype options'
                        defaultValue={radio_choice_searchtype}
                        name="searchtypebuttons"
                        onChange={handleChange}>

                        <FormControlLabel control={<Radio />} label="Default" value="DEFAULT" />
                        <FormControlLabel control={<Radio />} label="Proximity Search" value="PROXIMITY" />
                        <FormControlLabel control={<Radio />} label="Phrase Search" value="PHRASE" />
                        <FormControlLabel control={<Radio />} label="Author Search (By Last Name)" value="AUTHOR" disabled={props.datasets} />


                    </RadioGroup>
                </FormControl>
            </List>


            <Divider />
            <List>
            <FormControl sx = {{
          margin:2
        }}>
        <div style = {{
          display : "flex",
          flexDirection: "row"
        }}>
          <p style ={{
            color: "grey"
        }}>📅 Date Range:</p>
        </div>
        </FormControl>
                <div style={{

                    marginRight: "5em",
                    marginLeft: "1em"

                }}>
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <Stack spacing={3}>
                            <DesktopDatePicker
                                label="From"
                                inputFormat="dd/MM/yyyy"
                                value={fromDate}
                                onChange={(newfromvalue) => {
                                    setFromDate(newfromvalue);
                                    console.log(newfromvalue);
                                    handleChange();
                                }}
                                allowSameDateSelection
                                renderInput={(params) => <TextField {...params} />}
                            />
                            <DesktopDatePicker
                                label="To"
                                inputFormat="dd/MM/yyyy"
                                value={toDate}
                                onChange={(newtovalue) => {
                                    setToDate(newtovalue);
                                    handleChange();
                                }}
                                allowSameDateSelection
                                renderInput={(params) => <TextField {...params} />}
                            />
                        </Stack>
                    </LocalizationProvider>
                </div>
            </List>


            <Divider />
        </Box>
    );

    return (

        <div>
            <ThemeProvider theme={theme}>

                {['Advanced Options'].map((anchor) => (
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

            </ThemeProvider>
        </div>
    );
}
