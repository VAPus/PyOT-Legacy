function wgNiceNumber(number) {
   // Limit to 7 characters.
   if(number < 1000000) {
       return number;
   } else if(number >= 1000000000000000) {
       // QuadTrillion 123.45T
       // Limit is 1800 quintrillion. If we are above 1000 do extra precision.
       if(number >= 1000000000000000000) {
           return (number / 1000000000000000).toPrecision(6) + 'qT';
       } else {
           return (number / 1000000000000000).toPrecision(5) + 'qT';
       }
   } else if(number >= 1000000000000) {
       // Trillion 123.45T
       return (number / 1000000000000).toPrecision(5) + 'T';
   } else if(number >= 1000000000) {
       // Billion 123.45B
       return (number / 1000000000).toPrecision(5) + 'B';
   } else if(number >= 1000000) {
       // Million. 123.45M
       return (number / 1000000).toPrecision(5) + 'M';
   }
}
