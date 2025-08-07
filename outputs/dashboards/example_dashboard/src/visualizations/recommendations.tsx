import React from 'react';
import { Card, Title, Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell } from '@tremor/react';

interface recommendationsProps {
  data: any[];
  config: any;
}

export const recommendations: React.FC<recommendationsProps> = ({ data, config }) => {
  
  return (
    <Card>
      <Title>Recommendations</Title>
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            <TableHeaderCell>item</TableHeaderCell> <TableHeaderCell>score</TableHeaderCell> <TableHeaderCell>recommendation</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.slice(0, 10).map((item, idx) => (
            <TableRow key={idx}>
              <TableCell>{item.item}</TableCell> <TableCell>{item.score}</TableCell> <TableCell>{item.recommendation}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
};