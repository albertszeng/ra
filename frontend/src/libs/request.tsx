import { Game } from './game';
import { WarningLevel } from '../common';

type Visibility = 'PUBLIC' | 'PRIVATE';

type ActionRequest = {
  gameId: string;
  command: string;
};
type ActionResponse = {
  gameAsStr: string;
  gameState: Game;
  // The action performed.
  action: string;
  // Ther user (possibly an AI) that performed it.
  username: string;
};

type StartRequest = {
  numPlayers: number;
  visibility: Visibility;
};
type JoinLeaveRequest = {
  gameId: string;
};
type StartResponse = ActionResponse & JoinLeaveRequest;

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
  visibility: Visibility;
  numPlayers: number;
};
type ListGamesResponse = {
  partial: boolean;
  games: ListGame[];
};

type DeleteRequest = {
  gameId: string;
};

export type {
  ActionRequest,
  ApiResponse,
  DeleteRequest,
  JoinLeaveRequest,
  ListGame,
  ListGamesResponse,
  LoginOrRegisterRequest,
  LoginResponse,
  LoginSuccess,
  MessageResponse,
  StartRequest,
  StartResponse,
  TokenLoginRequest,
  Visibility,
  WarningLevel,
};
