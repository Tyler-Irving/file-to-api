import type { DatasetColumn } from '../types';

interface SchemaTableProps {
  columns: DatasetColumn[];
}

const typeColors: Record<string, string> = {
  text: 'bg-purple-100 text-purple-800',
  integer: 'bg-blue-100 text-blue-800',
  float: 'bg-cyan-100 text-cyan-800',
  boolean: 'bg-green-100 text-green-800',
  date: 'bg-orange-100 text-orange-800',
  datetime: 'bg-red-100 text-red-800',
};

export default function SchemaTable({ columns }: SchemaTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Column Name
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Field Name
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Type
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Nullable
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Sample Values
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {columns.map((column) => (
            <tr key={column.position} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-sm font-medium text-gray-900">
                {column.name}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600 font-mono">
                {column.field_name}
              </td>
              <td className="px-4 py-3 text-sm">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    typeColors[column.data_type] || 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {column.data_type}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {column.nullable ? 'Yes' : 'No'}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                <div className="flex flex-wrap gap-1">
                  {column.sample_values.slice(0, 3).map((value, idx) => (
                    <code
                      key={idx}
                      className="px-2 py-1 bg-gray-100 rounded text-xs"
                    >
                      {value === null || value === undefined ? 'null' : String(value)}
                    </code>
                  ))}
                  {column.sample_values.length > 3 && (
                    <span className="text-gray-400 text-xs">
                      +{column.sample_values.length - 3} more
                    </span>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
