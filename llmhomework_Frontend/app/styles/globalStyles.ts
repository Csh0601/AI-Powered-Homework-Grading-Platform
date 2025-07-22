import { StyleSheet } from 'react-native';
import { backgroundColor, errorColor, primaryColor, textColor } from './colors';

const globalStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: backgroundColor,
    padding: 16,
  },
  button: {
    backgroundColor: primaryColor,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  titleText: {
    fontSize: 22,
    fontWeight: 'bold',
    color: textColor,
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    padding: 10,
    fontSize: 16,
    color: textColor,
    backgroundColor: '#fafafa',
    marginBottom: 12,
  },
  errorText: {
    color: errorColor,
    fontSize: 14,
    marginTop: 4,
  },
});

export default globalStyles;
