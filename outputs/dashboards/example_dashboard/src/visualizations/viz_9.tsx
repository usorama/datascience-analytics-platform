import React from 'react';
import { ScatterChart, Card, Title } from '@tremor/react';

interface viz_9Props {
  data: any[];
  config: any;
}

export const viz_9: React.FC<viz_9Props> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>Correlation: alignment_score vs okr_contribution</Title>
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            <TableHeaderCell>alignment_score</TableHeaderCell> <TableHeaderCell>okr_contribution</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.slice(0, 10).map((item, idx) => (
            <TableRow key={idx}>
              <TableCell>{item.alignment_score}</TableCell> <TableCell>{item.okr_contribution}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
};