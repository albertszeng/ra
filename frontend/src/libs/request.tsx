import { Game } from './game';
import { WarningLevel } from '../common';

type ActionRequest = {
  gameId: string;
  command: string;
};
type ActionResponse = {
  gameAsStr: string;
  gameState: Game;
};

type StartRequest = {
  numPlayers: number;
  playerNames: string[];
};
type StartResponse = ActionResponse & {
  gameId: string;
};

type MessageResponse = {
  level: WarningLevel;
  message: string;
};
type ApiResponse = StartResponse & MessageResponse;

type LoginOrRegisterRequest = {
  username: string;
  password: string;
};
type TokenLoginRequest = {
  token: string;
};
type LoginResponse = {
  level: WarningLevel;
  message: string;
  token?: string;
  username?: string;
};
type LoginSuccess = {
  token: string;
  username: string;
};

type ListGame = {
  id: string;
  players: string[];
};
type ListGamesResponse = {
  total: number;
  games: ListGame[];
};

type DeleteRequest = {
  gameId: string;
};

export type {
  ActionRequest,
  ApiResponse,
  DeleteRequest,
  ListGame,
  ListGamesResponse,
  LoginOrRegisterRequest,
  LoginResponse,
  LoginSuccess,
  MessageResponse,
  StartRequest,
  StartResponse,
  TokenLoginRequest,
  WarningLevel,
};
