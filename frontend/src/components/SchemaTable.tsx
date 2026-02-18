import type { DatasetColumn } from '../types';

interface SchemaTableProps {
  columns: DatasetColumn[];
}

const typeColors: Record<string, string> = {
  text: 'bg-purple-900/50 text-purple-300',
  integer: 'bg-blue-900/50 text-blue-300',
  float: 'bg-cyan-900/50 text-cyan-300',
  boolean: 'bg-green-900/50 text-green-300',
  date: 'bg-orange-900/50 text-orange-300',
  datetime: 'bg-red-900/50 text-red-300',
};

export default function SchemaTable({ columns }: SchemaTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-700">
        <thead className="bg-gray-750">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">
              Column Name
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">
              Field Name
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">
              Type
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">
              Nullable
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">
              Sample Values
            </th>
          </tr>
        </thead>
        <tbody className="bg-gray-800 divide-y divide-gray-700">
          {columns.map((column) => (
            <tr key={column.position} className="hover:bg-gray-750">
              <td className="px-4 py-3 text-sm font-medium text-white">
                {column.name}
              </td>
              <td className="px-4 py-3 text-sm text-gray-300 font-mono">
                {column.field_name}
              </td>
              <td className="px-4 py-3 text-sm">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    typeColors[column.data_type] || 'bg-gray-700 text-gray-300'
                  }`}
                >
                  {column.data_type}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-300">
                {column.nullable ? 'Yes' : 'No'}
              </td>
              <td className="px-4 py-3 text-sm text-gray-300">
                <div className="flex flex-wrap gap-1">
                  {column.sample_values.slice(0, 3).map((value, idx) => (
                    <code
                      key={idx}
                      className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-200"
                    >
                      {value === null || value === undefined ? 'null' : String(value)}
                    </code>
                  ))}
                  {column.sample_values.length > 3 && (
                    <span className="text-gray-500 text-xs">
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
