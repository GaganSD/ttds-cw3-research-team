import * as React from 'react';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';

export default function DsPaperRadio(props) {
  
    return (
    <FormControl>
      <RadioGroup
        row
        aria-labelledby="demo-radio-buttons-group-label"
        defaultValue="Papers"
        name="ds or paper radio"
        onChange = {(e) => {
            props.parentCallback(e.target.value);
        }}
      >
        <FormControlLabel value="Papers" control={<Radio />} label="Papers" />
        <FormControlLabel value="DataSets" control={<Radio />} label="Datasets" />
      </RadioGroup>
    </FormControl>
  );
}