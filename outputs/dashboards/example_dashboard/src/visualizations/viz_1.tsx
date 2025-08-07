import React from 'react';
import { Card, Title } from '@tremor/react';

interface viz_1Props {
  data: any[];
  config: any;
}

export const viz_1: React.FC<viz_1Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>Confusion Matrix</Title>
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            <TableHeaderCell>actual</TableHeaderCell> <TableHeaderCell>predicted</TableHeaderCell> <TableHeaderCell>count</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.slice(0, 10).map((item, idx) => (
            <TableRow key={idx}>
              <TableCell>{item.actual}</TableCell> <TableCell>{item.predicted}</TableCell> <TableCell>{item.count}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
};