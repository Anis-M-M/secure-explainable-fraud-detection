package com.frauddetection.controller;

import com.frauddetection.dto.AuthResponse;
import com.frauddetection.dto.LoginRequest;
import com.frauddetection.dto.RegisterRequest;
import com.frauddetection.model.User;
import com.frauddetection.security.JwtTokenProvider;
import com.frauddetection.service.AuditService;
import com.frauddetection.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/auth")
@Slf4j
@RequiredArgsConstructor
@Tag(name = "Authentication", description = "Auth endpoints")
public class AuthController {

    private final AuthService authService;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider tokenProvider;
    private final AuditService auditService;

    @PostMapping("/register")
    @Operation(summary = "Register a new user")
    public ResponseEntity<AuthResponse.UserInfo> register(@Valid @RequestBody RegisterRequest request) {
        User user = authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(authService.toUserInfo(user));
    }

    @PostMapping("/login")
    @Operation(summary = "Login and get JWT token")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );

            String jwt = tokenProvider.generateToken(authentication);
            AuthResponse.UserInfo userInfo = authService.getUserByUsername(authentication.getName());

            auditService.logAction("LOGIN", "USER", authentication.getName(), "Successful login");

            return ResponseEntity.ok(AuthResponse.builder()
                    .token(jwt)
                    .tokenType("Bearer")
                    .expiresIn(86400)
                    .user(userInfo)
                    .build());

        } catch (Exception e) {
            log.warn("Login failed for user: {}", request.getUsername());
            auditService.logAction("LOGIN_FAILED", "USER", request.getUsername(), "Failed login attempt");
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid credentials");
        }
    }

    @PostMapping("/refresh")
    @Operation(summary = "Refresh JWT token")
    public ResponseEntity<AuthResponse> refreshToken(
            @RequestHeader("Authorization") String tokenHeader) {
        if (!StringUtils.hasText(tokenHeader) || !tokenHeader.startsWith("Bearer ")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing or invalid token");
        }

        String token = tokenHeader.substring(7);
        if (!tokenProvider.validateToken(token)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid token");
        }

        String username = tokenProvider.getUsernameFromJWT(token);
        String newToken = tokenProvider.generateTokenFromUsername(username);
        AuthResponse.UserInfo userInfo = authService.getUserByUsername(username);

        return ResponseEntity.ok(AuthResponse.builder()
                .token(newToken)
                .tokenType("Bearer")
                .expiresIn(86400)
                .user(userInfo)
                .build());
    }

    @GetMapping("/me")
    @Operation(summary = "Get current user profile")
    public ResponseEntity<AuthResponse.UserInfo> getCurrentUser(
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Authentication required");
        }
        return ResponseEntity.ok(authService.getUserByUsername(userDetails.getUsername()));
    }
}
