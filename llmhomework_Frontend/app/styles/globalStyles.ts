import { StyleSheet } from 'react-native';
import { 
  backgroundColor, 
  errorColor, 
  primaryColor, 
  textColor, 
  cardBackgroundColor,
  secondaryTextColor,
  borderColor,
  systemGray6
} from './colors';

const globalStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: backgroundColor,
    padding: 20,
  },
  card: {
    backgroundColor: cardBackgroundColor,
    borderRadius: 16,
    padding: 20,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  button: {
    backgroundColor: primaryColor,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#007AFF',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: primaryColor,
  },
  secondaryButtonText: {
    color: primaryColor,
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  titleText: {
    fontSize: 28,
    fontWeight: '700',
    color: textColor,
    marginBottom: 16,
    letterSpacing: -0.5,
  },
  subtitleText: {
    fontSize: 20,
    fontWeight: '600',
    color: textColor,
    marginBottom: 12,
    letterSpacing: -0.3,
  },
  bodyText: {
    fontSize: 17,
    fontWeight: '400',
    color: textColor,
    lineHeight: 24,
  },
  captionText: {
    fontSize: 15,
    fontWeight: '400',
    color: secondaryTextColor,
    lineHeight: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: borderColor,
    borderRadius: 12,
    padding: 16,
    fontSize: 17,
    color: textColor,
    backgroundColor: cardBackgroundColor,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  errorText: {
    color: errorColor,
    fontSize: 15,
    marginTop: 8,
    fontWeight: '500',
  },
  divider: {
    height: 1,
    backgroundColor: systemGray6,
    marginVertical: 16,
  },
  safeArea: {
    flex: 1,
    backgroundColor: backgroundColor,
  },
});

export default globalStyles;
